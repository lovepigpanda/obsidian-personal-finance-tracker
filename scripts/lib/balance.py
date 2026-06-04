"""
balance.py - 余额计算核心

路径 A（DataviewJS 仪表盘）和路径 B（Python 校验脚本）共用同一份算法。
这是保证两个独立计算路径结果一致的根本。

公式（每个账户、每种币种独立算）：
    balance(account, currency) = initial_balance
                              + sum(income where account=this and currency=this)
                              - sum(expense where account=this and currency=this)
                              - sum(transfer-out where from_account=this and currency=this)
                              + sum(transfer-in where to_account=this and currency=this)
"""

import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from .parsers import (
    find_transaction_files,
    parse_accounts,
    parse_frontmatter,
    file_status,
)


def compute_balances(vault_root: str) -> Dict[Tuple[str, str], float]:
    """
    计算每个 (账户, 币种) 的当前余额。

    Returns:
        {(account_name, currency): balance}
    """
    accounts = parse_accounts(vault_root)
    # 先用初始余额填 0
    balances = defaultdict(float)
    for name, info in accounts.items():
        balances[(name, info["currency"])] = info["initial_balance"]

    # 遍历所有交易
    for filepath in find_transaction_files(vault_root):
        if file_status(filepath) != "ACTIVE":
            continue
        fm, _ = parse_frontmatter(filepath)
        if not fm:
            continue

        tx_type = fm.get("type")
        amount = _safe_float(fm.get("amount"))
        currency = fm.get("currency", "CNY")
        if amount <= 0:
            continue

        if tx_type == "expense":
            account = fm.get("account")
            if account:
                balances[(account, currency)] -= amount

        elif tx_type == "income":
            account = fm.get("account")
            if account:
                balances[(account, currency)] += amount

        elif tx_type == "transfer" or tx_type == "transfer-out" or tx_type == "transfer-in":
            # 字段约定 (V1.3.4 build_frontmatter 真实产出):
            #   - out 文件: type=transfer-out, account=from, to_account=to
            #   - in  文件: type=transfer-in,  account=to,   to_account=from
            # 注意: build_frontmatter 只写 account + to_account (没有 from_account 字段),
            #       所以方向判断必须用 type 或 filepath, 不能用 from_account
            amount_currency = (fm.get("amount"), currency)
            if tx_type == "transfer-out" or "/transfers/out/" in filepath:
                # out 视角: account 字段就是 from 账户, 减钱
                from_acc = fm.get("account")
                if from_acc:
                    balances[(from_acc, currency)] -= amount
            elif tx_type == "transfer-in" or "/transfers/in/" in filepath:
                # in 视角: account 字段就是 to 账户, 加钱
                to_acc = fm.get("account")
                if to_acc:
                    balances[(to_acc, currency)] += amount
            else:
                # 兜底: 通用 "transfer" 类型 + 不在 out/in 目录 (项目里不会发生, 仅安全网)
                pass

    return dict(balances)


def compute_currency_totals(
    vault_root: str,
) -> Dict[str, Dict[str, float]]:
    """
    按币种汇总总流入、总流出（用于守恒检查）。

    Returns:
        {
            'CNY': {
                'income': 12345.0,
                'expense': 6789.0,
                'transfer_in': 5000.0,
                'transfer_out': 5000.0,
                'net_change': 1556.0,
            },
            ...
        }
    """
    totals = defaultdict(
        lambda: {"income": 0.0, "expense": 0.0, "transfer_in": 0.0, "transfer_out": 0.0}
    )

    for filepath in find_transaction_files(vault_root):
        if file_status(filepath) != "ACTIVE":
            continue
        fm, _ = parse_frontmatter(filepath)
        if not fm:
            continue

        tx_type = fm.get("type")
        amount = _safe_float(fm.get("amount"))
        currency = fm.get("currency", "CNY")
        if amount <= 0:
            continue

        if tx_type == "expense":
            totals[currency]["expense"] += amount
        elif tx_type == "income":
            totals[currency]["income"] += amount
        elif tx_type == "transfer":
            if "/transfers/out/" in filepath:
                totals[currency]["transfer_out"] += amount
            elif "/transfers/in/" in filepath:
                totals[currency]["transfer_in"] += amount

    # 加 net_change
    for ccy, data in totals.items():
        data["net_change"] = (
            data["income"] - data["expense"] - data["transfer_out"] + data["transfer_in"]
        )

    return dict(totals)


def _safe_float(v) -> float:
    """转 float，失败返 0。"""
    if v is None or v == "":
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


# ============================================================
# V1.4 增量余额快照 (Evan 需求: 每笔记账后实时刷新)
# ============================================================

def read_existing_balances(vault_root: str) -> Optional[Dict[Tuple[str, str], float]]:
    """
    从 Accounts/balances.md 读出当前快照的 {(account, currency): balance} 字典。

    Returns:
        - 成功: dict (可能为空 {})
        - 文件不存在 / 解析失败: None  (调用方应 fallback 到全量重算)

    实现说明:
        - 只解析 frontmatter (在 --- 块之间), 不解析 body 表格 (body 给人读, 不是真相源)
        - frontmatter 格式: balances 数组, 每项 4 字段 (account/currency/balance/type)
        - 账户名带中文/特殊字符, 用 _yaml_str() 转义 (跟 write_balance_snapshot 一致)
    """
    path = os.path.join(vault_root, "Accounts", "balances.md")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None

    # 提取 frontmatter 块 (第一个 --- 到下一个 --- 之间)
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not m:
        return None
    fm_text = m.group(1)

    # 解析 balances 数组 (YAML 简化为"裸"匹配, 不引 pyyaml 依赖, 跟现有风格一致)
    # 期待格式:
    #   balances:
    #     - account: "Alipay"
    #       currency: "CNY"
    #       balance: 123.45
    #       type: "e-wallet"
    result: Dict[Tuple[str, str], float] = {}

    # 逐行扫描, 累积当前账户/币种, 遇到 balance 行提交
    current_acc: Optional[str] = None
    current_ccy: Optional[str] = None
    in_balances = False
    for line in fm_text.split("\n"):
        stripped = line.strip()
        # 进入 balances 块
        if stripped == "balances:":
            in_balances = True
            continue
        # 离开 balances 块 (下一个顶级 key, 不以 "  -" 开头)
        if in_balances and stripped and not line.startswith(" "):
            in_balances = False
        if not in_balances:
            continue

        # 数组条目开始: "  - account: \"X\"" 或 "  - account: 'X'"
        m_acc = re.match(r'\s*-\s*account:\s*["\']([^"\']+)["\']', line)
        if m_acc:
            current_acc = m_acc.group(1)
            current_ccy = None
            continue
        m_ccy = re.match(r'\s*currency:\s*["\']([^"\']+)["\']', line)
        if m_ccy:
            current_ccy = m_ccy.group(1)
            continue
        m_bal = re.match(r"\s*balance:\s*([-\d.]+)", line)
        if m_bal and current_acc and current_ccy:
            try:
                result[(current_acc, current_ccy)] = float(m_bal.group(1))
            except ValueError:
                pass
            # 重置, 防下一个条目误用
            current_acc = None
            current_ccy = None
    return result


def merge_balances(
    existing: Dict[Tuple[str, str], float],
    new_full: Dict[Tuple[str, str], float],
    affected_accounts: set,
) -> Dict[Tuple[str, str], float]:
    """
    合并旧快照和全量重算结果:
    - 受影响账户: 用 new_full 的值
    - 未受影响账户: 用 existing 的值 (避免无谓重算)
    - 只在 new_full 里、affected 里的新账户: 也要加进 merged (新建账户场景)

    Args:
        existing: 旧 balances.md 读出来的 { (acc, ccy): bal }
        new_full: compute_balances() 全量重算结果
        affected_accounts: 写笔后受影响的账户名 set (e.g. {"Alipay"} 或 {"Alipay","CMB"})

    Returns:
        合并后的 { (acc, ccy): bal }
    """
    merged: Dict[Tuple[str, str], float] = {}
    # 受影响用新值
    for (acc, ccy), bal in new_full.items():
        if acc in affected_accounts:
            merged[(acc, ccy)] = bal
    # 不受影响用旧值
    for (acc, ccy), bal in existing.items():
        if acc not in affected_accounts:
            merged[(acc, ccy)] = bal
    # 兜底: 旧里有但新里没有 (理论上不该发生, 但防御) + 新里有但旧里没有
    for (acc, ccy), bal in new_full.items():
        if (acc, ccy) not in merged:
            merged[(acc, ccy)] = bal
    return merged


def render_balance_snapshot(
    balances: Dict[Tuple[str, str], float],
    source: str,
    total_accounts: Optional[int] = None,
    total_currencies: Optional[int] = None,
) -> str:
    """
    把 { (acc, ccy): bal } 字典渲染成 balances.md 完整内容 (frontmatter + body)。

    这是 write_balance_snapshot 的纯渲染版本, 不读 vault 不写文件, 方便复用/测试。

    Args:
        balances: 已合并的 { (acc, ccy): bal }
        source: "daily_integrity_check.py" / "transaction_create.py" / "incremental"
        total_accounts: 账户数 (默认 = len(balances), 因每账户通常只 1 个币种)
        total_currencies: 币种数 (默认自动从 balances 推)

    Returns:
        markdown 文本
    """
    if not balances:
        return ""

    def _yaml_str(s: str) -> str:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    # frontmatter balances 数组
    fm_lines = []
    for (acc, ccy), bal in sorted(balances.items()):
        fm_lines.append(f"  - account: {_yaml_str(acc)}")
        fm_lines.append(f"    currency: {_yaml_str(ccy)}")
        fm_lines.append(f"    balance: {bal:.2f}")
    fm_balances = "\n".join(fm_lines)

    # frontmatter totals_by_currency
    by_ccy: Dict[str, float] = defaultdict(float)
    for (acc, ccy), bal in balances.items():
        by_ccy[ccy] += bal
    fm_totals = "\n".join(f"  {ccy}: {total:.2f}" for ccy, total in sorted(by_ccy.items()))

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    n_acc = total_accounts if total_accounts is not None else len(balances)
    n_ccy = total_currencies if total_currencies is not None else len(by_ccy)

    # 人类可读表格
    body_rows = []
    for (acc, ccy), bal in sorted(balances.items()):
        body_rows.append(f"| {acc} | {ccy} | {bal:,.2f} |")
    body_table = "\n".join(body_rows)

    content = (
        "---\n"
        'title: "Account Balance Snapshot — 账户余额快照"\n'
        "type: balance-snapshot\n"
        f'generated: "{timestamp}"\n'
        f"source: {source}\n"
        f"total_accounts: {n_acc}\n"
        f"total_currencies: {n_ccy}\n"
        "balances:\n"
        f"{fm_balances}\n"
        "totals_by_currency:\n"
        f"{fm_totals}\n"
        "---\n\n"
        "# 账户余额快照\n\n"
        f"> 此文件由 `scripts/{source}` 自动生成, **不要手动编辑**。\n"
        ">\n"
        f"> 生成时间: {timestamp}\n"
        f"> 账户数: {n_acc} · 币种数: {n_ccy}\n"
        "> 数据源: Python `compute_balances()` 完整扫描 + 累加\n\n"
        "---\n\n"
        "## 各账户余额 (人类可读)\n\n"
        "| 账户 | 币种 | 余额 |\n"
        "|------|------|------|\n"
        f"{body_table}\n\n"
        "---\n\n"
        "## Dataview 提示\n\n"
        "仪表盘 `Dashboards/finance-dashboard.md` 读 `type = balance-snapshot` 的 frontmatter `balances` 数组。\n"
        "要强制刷新: 跑一次 `python3 scripts/daily_integrity_check.py --vault ~/Obsidian/finance`\n"
    )
    return content


def write_balance_snapshot(
    vault_root: str,
    source: str = "daily_integrity_check.py",
) -> str:
    """
    把当前 compute_balances() 的结果写到 Accounts/balances.md 快照。
    Dataview 仪表盘只读这个文件, 不再每次全扫描 Transactions/。

    V1.4 修订: 加 source 参数, 支持 transaction_create.py 写笔后增量调用。
              同一份渲染逻辑, 全量和增量都走 render_balance_snapshot()。

    格式: frontmatter (YAML 数组 + 字典, 给 Dataview 解析) + 表格 body (人类可读)
    写盘策略: 每次覆盖, 不追加 — 余额是"当前状态"不是"事件流"。
    返回: 写入的绝对路径, 失败返回 ""。
    """
    balances = compute_balances(vault_root)
    if not balances:
        return ""
    content = render_balance_snapshot(balances, source=source)
    if not content:
        return ""
    out_path = os.path.join(vault_root, "Accounts", "balances.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    return out_path


def refresh_balance_snapshot_incremental(
    vault_root: str,
    affected_accounts: set,
    source: str = "transaction_create.py",
) -> str:
    """
    V1.4 新增: 写笔后增量刷新余额快照。

    行为:
    1. 读现有 balances.md → existing dict (失败返 None 时 fallback 全量)
    2. compute_balances() 全量重算 (O(N), 但只算一次, 跟 daily 一致)
    3. 合并: 受影响账户用新值, 其他用旧值
    4. 渲染 + 写盘, source="transaction_create.py"

    为什么不"严格 O(1)":
    - compute_balances 算单个账户余额需要扫全 Transactions (因为收入/支出可能分布在多个文件)
    - 真正"省"的是: 避免重读 parse_accounts + 重算所有未受影响账户的累加
    - 在 N=几十笔的规模下, 增量 vs 全量时间差 < 1ms, 实际价值不在性能, 在"语义清晰":
      * 写笔后 balances.md mtime 立刻变 (用户感知"实时")
      * source 字段告诉用户"这次刷新是写笔触发的" (审计清晰)
      * transfer 触发时, 显式记录 from/to 都被刷 (不是静默全量)

    Args:
        vault_root: vault 根目录
        affected_accounts: 受影响账户名 set (e.g. {"Alipay"} 或 {"Alipay","CMB"} for transfer)
        source: 写入 frontmatter 的 source 字段

    Returns:
        写入路径, 失败 ""
    """
    if not affected_accounts:
        # 安全网: 调用方忘了传受影响账户, fallback 全量
        return write_balance_snapshot(vault_root, source=source)

    # 1. 读旧快照
    existing = read_existing_balances(vault_root)

    # 2. 全量重算
    new_full = compute_balances(vault_root)
    if not new_full:
        return ""

    # 3. 合并
    if existing is None:
        # 旧快照不存在/损坏, 用全量
        merged = new_full
    else:
        merged = merge_balances(existing, new_full, affected_accounts)

    # 4. 渲染 + 写盘
    content = render_balance_snapshot(merged, source=source)
    if not content:
        return ""
    out_path = os.path.join(vault_root, "Accounts", "balances.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    return out_path
