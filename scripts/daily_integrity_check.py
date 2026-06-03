#!/usr/bin/env python3
"""
daily_integrity_check.py - 每日完整性检查

用法:
    python3 daily_integrity_check.py [--vault <vault_root>]

检查内容:
    1. 每币种的 income == transfer_in (流入部分)
    2. 每币种的 expense == transfer_out (流出部分)
       (实际只校验 transfer 的 out/in 平衡,不直接对账 income/expense, 那些是用户行为)
    3. 所有 transfer 的 out 和 in 文件配对完整 (转移的"账面"自洽)
    4. 每个账户余额变化 == 该账户所有交易的净影响 (路径A vs 路径B 自洽)
    5. 账户表里的初始余额非负且合理 (sanity check)
    6. 没有任何孤立的 transfer_pair_id (只有 out 没有 in, 或反过来)
    7. #33 记账频率分析 (过去 7 天活跃天数 / 笔数, 漏记检测)
    8. #34 账户遗忘检测 (距每个账户最后一笔 > 14 天报 WARN)
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import (
    find_transaction_files,
    parse_frontmatter,
    parse_accounts,
    find_transfer_pair,
    file_status,
)
from lib.balance import compute_balances, compute_currency_totals
from lib.notifier import notify


def check_transfer_pairing(vault_root: str) -> list:
    """
    校验所有 transfer 的 out 和 in 都成对存在。
    返回 error 列表: [(level, message), ...]
    """
    errors = []
    base = os.path.join(vault_root, "Transactions", "transfers")
    if not os.path.isdir(base):
        return errors

    out_dir = os.path.join(base, "out")
    in_dir = os.path.join(base, "in")

    # 收集所有 pair_id
    out_pairs = {}  # pair_id -> file
    in_pairs = {}

    for d, target in [(out_dir, out_pairs), (in_dir, in_pairs)]:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if not f.endswith(".md"):
                continue
            fp = os.path.join(d, f)
            fm, _ = parse_frontmatter(fp)
            pair_id = fm.get("transfer_pair_id")
            status = file_status(fp)
            if status != "ACTIVE":
                continue
            if not pair_id:
                errors.append(("ERROR", f"{f}: transfer 缺少 transfer_pair_id"))
                continue
            if pair_id in target:
                errors.append(("WARN", f"{f}: transfer_pair_id '{pair_id}' 重复"))
            target[pair_id] = fp

    # out 和 in 是否一一对应
    for pair_id in out_pairs:
        if pair_id not in in_pairs:
            errors.append(("ERROR", f"transfer 配对缺失: {os.path.basename(out_pairs[pair_id])} (pair_id={pair_id}) 没有对应的 in/ 文件"))
    for pair_id in in_pairs:
        if pair_id not in out_pairs:
            errors.append(("ERROR", f"transfer 配对缺失: {os.path.basename(in_pairs[pair_id])} (pair_id={pair_id}) 没有对应的 out/ 文件"))

    # 已配对的: 字段一致性
    for pair_id in out_pairs:
        if pair_id not in in_pairs:
            continue
        ofm, _ = parse_frontmatter(out_pairs[pair_id])
        ifm, _ = parse_frontmatter(in_pairs[pair_id])

        if float(ofm.get("amount", 0)) != float(ifm.get("amount", 0)):
            errors.append((
                "ERROR",
                f"transfer 配对金额不一致 (pair_id={pair_id}): out={ofm.get('amount')}, in={ifm.get('amount')}",
            ))
        if ofm.get("currency") != ifm.get("currency"):
            errors.append((
                "ERROR",
                f"transfer 配对币种不一致 (pair_id={pair_id}): out={ofm.get('currency')}, in={ifm.get('currency')}",
            ))
        # out 和 in 的 from/to 必须完全一致 (同一笔交易, 语义统一)
        if ofm.get("from_account") != ifm.get("from_account") or ofm.get("to_account") != ifm.get("to_account"):
            errors.append((
                "ERROR",
                f"transfer 配对账户不一致 (pair_id={pair_id}): out 是 {ofm.get('from_account')}→{ofm.get('to_account')}, in 是 {ifm.get('from_account')}→{ifm.get('to_account')}",
            ))

    return errors


def check_currency_conservation(vault_root: str) -> list:
    """
    检查每币种的 transfer_in == transfer_out (转账自洽)。
    """
    errors = []
    totals = compute_currency_totals(vault_root)
    for ccy, data in totals.items():
        tin = data.get("transfer_in", 0.0)
        tout = data.get("transfer_out", 0.0)
        if abs(tin - tout) > 0.001:  # 浮点容差
            errors.append((
                "ERROR",
                f"{ccy}: transfer 流入 ({tin}) ≠ 流出 ({tout}), 差 {tin - tout:.2f}",
            ))
    return errors


def check_balances_self_consistent(vault_root: str) -> list:
    """
    校验 compute_balances 的结果 = (初始 + 所有交易净影响)
    这是路径A vs 路径B 的一致性 (Python 自检, 不依赖 Dataview)。
    """
    errors = []
    accounts = parse_accounts(vault_root)
    balances = compute_balances(vault_root)

    # 重新按交易类型累加
    expected = defaultdict(float)
    for name, info in accounts.items():
        expected[(name, info["currency"])] = info["initial_balance"]

    for filepath in find_transaction_files(vault_root):
        if file_status(filepath) != "ACTIVE":
            continue
        fm, _ = parse_frontmatter(filepath)
        if not fm:
            continue
        tx_type = fm.get("type")
        amount = float(fm.get("amount", 0) or 0)
        ccy = fm.get("currency", "CNY")
        if amount <= 0:
            continue

        if tx_type == "expense":
            acc = fm.get("account")
            if acc:
                expected[(acc, ccy)] -= amount
        elif tx_type == "income":
            acc = fm.get("account")
            if acc:
                expected[(acc, ccy)] += amount
        elif tx_type == "transfer":
            if "/transfers/out/" in filepath:
                acc = fm.get("from_account")
                if acc:
                    expected[(acc, ccy)] -= amount
            elif "/transfers/in/" in filepath:
                acc = fm.get("to_account")
                if acc:
                    expected[(acc, ccy)] += amount

    # 对比
    keys = set(balances.keys()) | set(expected.keys())
    for key in keys:
        b = balances.get(key, 0.0)
        e = expected.get(key, 0.0)
        if abs(b - e) > 0.001:
            errors.append((
                "ERROR",
                f"余额计算自检失败: {key[0]}/{key[1]}: compute_balances={b:.2f} 累加={e:.2f} 差 {b - e:.2f}",
            ))
    return errors


def check_negative_balances(vault_root: str) -> list:
    """
    检查账户余额为负数 (可能透支)。

    ⚠️ 豁免以下账户类型 (它们的余额**本应**是负数):
    - credit-card: 信用卡, 负数=欠款
    - loan: 贷款账户, 负数=未还本金
    """
    errors = []
    balances = compute_balances(vault_root)
    accounts = parse_accounts(vault_root)

    for (acc, ccy), bal in balances.items():
        if bal < -0.01:
            # 检查账户类型, 豁免正常负债账户
            acc_type = accounts.get(acc, {}).get("type", "")
            if acc_type in ("credit-card", "loan"):
                # 负债账户, 负数正常, 跳过透支检查
                continue
            errors.append((
                "WARN",
                f"账户 {acc} ({ccy}) 余额为负: {bal:.2f}",
            ))
    return errors


def check_bookkeeping_frequency(vault_root: str, days: int = 7) -> list:
    """
    #33 记账频率分析。

    扫描过去 N 天 (默认 7) 的交易, 统计:
    - 活跃天数 (有交易的不同日期数)
    - 交易笔数
    - 漏记检测: 如果 N 天内 0 笔, 但账户余额非零, 报 WARN
      ("你这周没记账, 但账户余额 X, 打开银行 App 核对一下")
    """
    from datetime import date, timedelta

    errors = []
    today = date.today()
    cutoff = today - timedelta(days=days)

    active_dates = set()
    tx_count = 0

    for filepath in find_transaction_files(vault_root):
        if file_status(filepath) != "ACTIVE":
            continue
        fm, _ = parse_frontmatter(filepath)
        if not fm:
            continue
        d_str = str(fm.get("date", ""))
        try:
            d = date.fromisoformat(d_str)
        except (ValueError, TypeError):
            continue
        if d >= cutoff:
            active_dates.add(d)
            tx_count += 1

    if tx_count == 0:
        # 漏记检测: 0 笔 + 账户有非零余额 = 可疑
        balances = compute_balances(vault_root)
        non_zero_count = sum(1 for b in balances.values() if abs(b) > 0.01)
        if non_zero_count > 0:
            errors.append((
                "WARN",
                f"过去 {days} 天 0 笔记账 (账户 {non_zero_count} 个有余额), "
                f"建议打开银行 App 核对实际交易, 是否有漏记"
            ))
    else:
        # 正常: 仅做 INFO 输出
        pass

    # 把统计写进 details 备用 (main 用)
    errors.append((
        "INFO",
        f"过去 {days} 天记账: {tx_count} 笔 / 活跃 {len(active_dates)} 天"
    ))
    return errors


def check_account_inactivity(vault_root: str, days: int = 14) -> list:
    """
    #34 账户遗忘检测。

    对每个账户: 距最后一笔交易 > N 天 (默认 14) 报 WARN
    ("账户 X 已 18 天无变动, 这个账户还在用吗?")
    """
    from datetime import date

    errors = []
    accounts = parse_accounts(vault_root)
    if not accounts:
        return errors

    # 收集每个账户最后活跃日期
    last_active = {}  # (account, currency) -> date
    for filepath in find_transaction_files(vault_root):
        if file_status(filepath) != "ACTIVE":
            continue
        fm, _ = parse_frontmatter(filepath)
        if not fm:
            continue
        d_str = str(fm.get("date", ""))
        try:
            d = date.fromisoformat(d_str)
        except (ValueError, TypeError):
            continue

        ccy = fm.get("currency", "CNY")
        tx_type = fm.get("type")

        if tx_type in ("expense", "income"):
            acc = fm.get("account")
            if acc:
                key = (acc, ccy)
                if key not in last_active or d > last_active[key]:
                    last_active[key] = d
        elif tx_type == "transfer":
            if "/transfers/out/" in filepath:
                acc = fm.get("from_account")
            elif "/transfers/in/" in filepath:
                acc = fm.get("to_account")
            else:
                acc = None
            if acc:
                key = (acc, ccy)
                if key not in last_active or d > last_active[key]:
                    last_active[key] = d

    today = date.today()
    for (acc, ccy), d in last_active.items():
        gap = (today - d).days
        if gap > days:
            errors.append((
                "WARN",
                f"账户 {acc} ({ccy}) 已 {gap} 天无变动, 这个账户还在用吗?"
            ))

    return errors


def write_balance_snapshot(vault_root: str) -> str:
    """
    把当前 compute_balances() 的结果写到 Accounts/balances.md 快照。
    Dataview 仪表盘只读这个文件, 不再每次全扫描 Transactions/。

    格式: frontmatter (YAML 数组 + 字典, 给 Dataview 解析) + 表格 body (人类可读)
    写盘策略: 每次覆盖, 不追加 — 余额是"当前状态"不是"事件流"。
    返回: 写入的绝对路径, 失败返回 ""。
    """
    balances = compute_balances(vault_root)
    accounts = parse_accounts(vault_root)
    if not balances:
        return ""

    def _yaml_str(s: str) -> str:
        """YAML 字符串转义 (账户名有中文/特殊字符)。"""
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    # frontmatter balances 数组
    fm_lines = []
    for (acc, ccy), bal in sorted(balances.items()):
        acc_type = accounts.get(acc, {}).get("type", "")
        fm_lines.append(f"  - account: {_yaml_str(acc)}")
        fm_lines.append(f"    currency: {_yaml_str(ccy)}")
        fm_lines.append(f"    balance: {bal:.2f}")
        if acc_type:
            fm_lines.append(f"    type: {_yaml_str(acc_type)}")
    fm_balances = "\n".join(fm_lines)

    # frontmatter totals_by_currency 字典
    by_ccy = defaultdict(float)
    for (acc, ccy), bal in balances.items():
        by_ccy[ccy] += bal
    fm_totals = "\n".join(
        f"  {ccy}: {total:.2f}" for ccy, total in sorted(by_ccy.items())
    )

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    total_accounts = len(balances)
    total_ccy = len(by_ccy)

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
        "source: daily_integrity_check.py\n"
        f"total_accounts: {total_accounts}\n"
        f"total_currencies: {total_ccy}\n"
        "balances:\n"
        f"{fm_balances}\n"
        "totals_by_currency:\n"
        f"{fm_totals}\n"
        "---\n\n"
        "# 账户余额快照\n\n"
        "> 此文件由 `scripts/daily_integrity_check.py` 自动生成, **不要手动编辑**。\n"
        ">\n"
        f"> 生成时间: {timestamp}\n"
        f"> 账户数: {total_accounts} · 币种数: {total_ccy}\n"
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

    out_path = os.path.join(vault_root, "Accounts", "balances.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="每日财务完整性检查")
    ap.add_argument(
        "--vault",
        default=os.path.expanduser("~/Obsidian/finance"),
        help="vault 根目录",
    )
    ap.add_argument(
        "--no-notify",
        action="store_true",
        help="不写 alerts.md 和不发送通知",
    )
    args = ap.parse_args()

    vault = os.path.abspath(os.path.expanduser(args.vault))

    all_errors = []
    print("🔍 1/6 检查转账配对完整性...")
    all_errors += check_transfer_pairing(vault)
    print("🔍 2/6 检查币种转账守恒...")
    all_errors += check_currency_conservation(vault)
    print("🔍 3/6 检查余额计算自洽...")
    all_errors += check_balances_self_consistent(vault)
    print("🔍 4/6 检查账户透支...")
    all_errors += check_negative_balances(vault)
    print("🔍 5/6 #33 检查记账频率分析...")
    all_errors += check_bookkeeping_frequency(vault)
    print("🔍 6/6 #34 检查账户遗忘检测...")
    all_errors += check_account_inactivity(vault)
    print("💾 7/7 写余额快照到 Accounts/balances.md...")
    snapshot_path = write_balance_snapshot(vault)
    if snapshot_path:
        print(f"   快照写入: {snapshot_path}")
    else:
        print("   ⚠️  无账户数据, 跳过快照")

    if not all_errors:
        print("\n✅ 所有检查通过 — 财务系统内部一致")
        # 即使通过也写一条 INFO 到 alerts.md (审计痕迹)
        if not args.no_notify:
            from lib.notifier import write_alert
            write_alert(
                vault,
                title="每日完整性检查通过",
                severity="INFO",
                details=["6 项检查全部通过", f"账户数: {len(compute_balances(vault))}"],
                source="daily_integrity_check.py",
            )
        sys.exit(0)

    # INFO 不算 error/warn, 过滤掉后再判断
    actionable = [(l, m) for l, m in all_errors if l in ("ERROR", "WARN")]
    if not actionable:
        # 只有 INFO, 视为通过
        print(f"\n✅ 6 项检查通过 — {len(all_errors)} 条信息")
        if not args.no_notify:
            from lib.notifier import write_alert
            write_alert(
                vault,
                title="每日完整性检查通过",
                severity="INFO",
                details=[f"[{l}] {m}" for l, m in all_errors],
                source="daily_integrity_check.py",
            )
        sys.exit(0)

    has_error = any(level == "ERROR" for level, _ in actionable)
    severity = "ERROR" if has_error else "WARN"

    print(f"\n{'❌' if has_error else '⚠️ '}  发现 {len(actionable)} 个问题")
    for level, msg in actionable:
        marker = "  ❌" if level == "ERROR" else "  ⚠️ "
        print(f"{marker} [{level}] {msg}")
    # INFO 一并展示
    for level, msg in all_errors:
        if level == "INFO":
            print(f"  ℹ️  [{level}] {msg}")

    if not args.no_notify:
        details = [f"[{level}] {msg}" for level, msg in all_errors]
        notify(
            vault_root=vault,
            title=f"每日完整性检查{'失败' if has_error else '告警'}",
            body=f"发现 {len(actionable)} 个问题",
            severity=severity,
            details=details,
            source="daily_integrity_check.py",
        )

    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
