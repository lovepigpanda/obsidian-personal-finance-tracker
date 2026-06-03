"""
transaction_create.py — Agent 记账入口 (V1.3.3 #38 默认账户)

输入: Agent 解析用户自然语言得到:
  - type: expense | income | transfer
  - date: YYYY-MM-DD
  - amount: float
  - currency: CNY (默认)
  - category: 类别 (e.g. "Food", "Transport")
  - note: 备注
  - account: 可选 (用户已指定)
  - to_account: 仅 transfer
  - transfer_pair_id: 仅 transfer (Agent 生成)

流程:
  1. 解析账户列表
  2. 解析 config + learning
  3. 解析默认账户 (resolver)
  4. 若 learning 提示冲突 → 输出 ask_message (Agent 用 clarify 工具)
  5. 静默记录到 learning
  6. 创建 .md 交易文件
  7. 输出结果

用法:
  python3 transaction_create.py --vault /path/to/finance --type expense \
    --date 2026-06-03 --amount 45 --category Food --note "午餐沙县"
  # 输出 JSON: {file_path, account, source, ask_message?}
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import parse_accounts
from lib.default_account_resolver import (
    load_config,
    resolve_default_account,
    get_fallback,
)
from lib.learning_tracker import (
    load_learning,
    record_usage,
    confirm_update,
    extract_keywords,
)


DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, "..", "config", "default_accounts.yaml")


def generate_filename(type_: str, date_: str, description: str, amount: float, currency: str) -> str:
    """生成交易文件名: YYYY-MM-DD-{description}-{amount}-{CURRENCY}-ACTIVE.md"""
    safe_desc = re.sub(r"[^\w\u4e00-\u9fff-]", "-", description or "tx")
    safe_desc = re.sub(r"-+", "-", safe_desc).strip("-")
    if not safe_desc:
        safe_desc = "tx"
    return f"{date_}-{safe_desc}-{amount}-{currency}-ACTIVE.md"


def build_frontmatter(
    type_: str,
    date_: str,
    amount: float,
    currency: str,
    category: str,
    account: str,
    note: str,
    to_account: Optional[str] = None,
    transfer_pair_id: Optional[str] = None,
) -> str:
    """生成 YAML frontmatter。"""
    lines = [
        "---",
        f"type: {type_}",
        f"date: {date_}",
        f"amount: {amount}",
        f"currency: {currency}",
        f"category: {category}",
        f"account: {account}",
        f"payment_method: {account}",
        f'note: "{note}"',
        "tags: [transaction, auto-created]",
        "status: ACTIVE",
        f"created: {date_}",
    ]
    if to_account:
        lines.append(f"to_account: {to_account}")
    if transfer_pair_id:
        lines.append(f"transfer_pair_id: {transfer_pair_id}")
    lines.append("---")
    return "\n".join(lines)


def build_body(type_: str, date_: str, amount: float, currency: str, category: str, account: str, note: str, to_account: Optional[str] = None) -> str:
    """生成交易正文 (markdown table)."""
    type_zh = {"expense": "支出", "income": "收入", "transfer": "转账"}.get(type_, type_)

    rows = [
        f"# {date_} — {type_zh} (Agent 自动)",
        "",
        "| 字段 | 值 |",
        "|------|---|",
        f"| **类型** | {type_zh} |",
        f"| **日期** | {date_} |",
        f"| **金额** | {amount} {currency} |",
        f"| **类别** | {category} |",
        f"| **账户** | {account} |",
    ]
    if to_account:
        rows.append(f"| **转入账户** | {to_account} |")
    rows.append(f"| **备注** | {note} |")
    rows.append("")
    return "\n".join(rows)


def create_transaction(
    vault_root: str,
    type_: str,
    date_: str,
    amount: float,
    currency: str = "CNY",
    category: str = "",
    note: str = "",
    account: Optional[str] = None,
    to_account: Optional[str] = None,
    transfer_pair_id: Optional[str] = None,
    config_path: str = DEFAULT_CONFIG_PATH,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    创建交易记录, 返回结构化结果。

    返回结构 (V1.3.4 修订):
      成功: {"ok": True, "file_path": str, "account": str, "source": str,
             "ask_message": Optional[str], "transfer_pair_id"?: str}
      失败: {"ok": False, "type": "error" | "ask", "message": str,
             "ask_message"?: str}    # type="ask" → 软告警, Agent 询问用户
                                    # type="error" → 硬错误, Agent 中止
    """
    # 1. 解析账户
    accounts = parse_accounts(vault_root)
    account_names = list(accounts.keys())

    # 2. 加载 config + learning
    config = load_config(config_path)
    store_path = config.get("learning", {}).get(
        "store_path", "~/.obsidian-finance/learning.json"
    )
    store_path = os.path.expanduser(store_path)
    learning = load_learning(store_path)

    # 3. 特殊: transfer 类型必须显式 from/to
    if type_ == "transfer":
        if not account or not to_account:
            return {
                "ok": False,
                "type": "error",
                "message": "transfer 类型必须显式提供 --account (from) 和 --to-account (to)",
            }
        # 验证 from/to 都已在 account-list.md
        if account not in account_names:
            return {
                "ok": False,
                "type": "error",
                "message": f"from 账户 '{account}' 不在 account-list.md (已注册: {account_names})",
            }
        if to_account not in account_names:
            return {
                "ok": False,
                "type": "error",
                "message": f"to 账户 '{to_account}' 不在 account-list.md (已注册: {account_names})",
            }
        # transfer 不走 default resolver, 直接用 from/to
        final_account = account
        to_account_final = to_account
        source = "user"
    else:
        # expense/income 走默认账户解析
        # 先校验: 用户显式给的账户必须存在 (V1.3.4 修复: 之前 silent fallback 会污染数据)
        if account and account not in account_names:
            return {
                "ok": False,
                "type": "error",
                "message": f"--account '{account}' 不在 account-list.md (已注册: {account_names})。请检查账户名拼写或更新 account-list.md",
            }
        resolved = resolve_default_account(
            category=category,
            note=note,
            account_names=account_names,
            config=config,
            learning=learning,
            user_provided_account=account,
        )
        final_account = resolved.get("account")
        source = resolved.get("source")
        to_account_final = None

        if not final_account:
            return {
                "ok": False,
                "type": "ask",
                "ask_message": resolved.get("ask_message", "无法确定账户, 请用户指定"),
            }

        # 验证解析出来的账户在 account-list.md (防御性, 防止 config 配错账户名)
        if final_account not in account_names:
            return {
                "ok": False,
                "type": "error",
                "message": f"解析出的账户 '{final_account}' 不在 account-list.md (source={source})。请检查 config/default_accounts.yaml 或 account-list.md",
            }

    # 4. learning 冲突检查 (仅当 account 是自动解析的, 不是用户显式指定)
    ask_message = None
    if type_ != "transfer" and source in ("config", "learning", "fallback", "note") and final_account:
        conflict, _learning_after = record_usage(
            store_path=store_path,
            category=category,
            note=note,
            account=final_account,
        )
        if conflict:
            ask_message = conflict

    # 5. 决定文件路径 + 描述
    description = note or category or "tx"

    if type_ == "expense":
        rel_paths = [os.path.join("Transactions/expenses", generate_filename(type_, date_, description, amount, currency))]
        # expense/income 写到 out 子目录 (历史习惯)
        rel_paths = [os.path.join("Transactions/expenses", generate_filename(type_, date_, description, amount, currency))]
    elif type_ == "income":
        rel_paths = [os.path.join("Transactions/incomes", generate_filename(type_, date_, description, amount, currency))]
    elif type_ == "transfer":
        # transfer 必须同时写 out + in 两个文件 (V1.3.4 修复: 之前只写 out 配对校验会失败)
        # out 文件: from=final_account, to=to_account
        out_filename = generate_filename(type_, date_, f"transfer-out-{final_account}-to-{to_account_final}", amount, currency)
        in_filename = generate_filename(type_, date_, f"transfer-in-{to_account_final}-from-{final_account}", amount, currency)
        rel_paths = [
            os.path.join("Transactions/transfers/out", out_filename),
            os.path.join("Transactions/transfers/in", in_filename),
        ]
        # 如果用户没提供 transfer_pair_id, 自动生成
        if not transfer_pair_id:
            import hashlib
            transfer_pair_id = "T-" + date_ + "-" + hashlib.md5(f"{date_}{final_account}{to_account_final}{amount}".encode()).hexdigest()[:8]
    else:
        return {
            "ok": False,
            "type": "error",
            "message": f"未知 type: {type_} (支持 expense/income/transfer)",
        }

    # 6. 检查同名文件 (soft alert: 保留旧文件, ask 用户 fix/ignore/delete)
    existing = [p for p in rel_paths if os.path.exists(os.path.join(vault_root, p))]
    if existing:
        return {
            "ok": False,
            "type": "ask",
            "ask_message": f"文件已存在, 不覆盖: {existing}。要 (1) 改描述/时间重命名  (2) 删除原文件  (3) 忽略这次记账  ?",
        }

    # 7. 生成内容
    written_paths = []
    for i, rel_path in enumerate(rel_paths):
        # transfer 的 out/in 共享 transfer_pair_id, 各自的 from/to 不同
        # 注: Pyright 看不到 type narrowing, 这里用 assert 显式声明
        assert final_account is not None, "final_account 在此处必非 None"
        if type_ == "transfer":
            assert to_account_final is not None, "to_account_final 在 transfer 类型必非 None"
            if "/out/" in rel_path:
                fm_account, fm_to_account = final_account, to_account_final
                this_type = "transfer-out"
            else:  # /in/
                fm_account, fm_to_account = to_account_final, final_account
                this_type = "transfer-in"
        else:
            fm_account = final_account
            fm_to_account = None
            this_type = type_

        fm = build_frontmatter(
            type_=this_type,
            date_=date_,
            amount=amount,
            currency=currency,
            category=category,
            account=fm_account,
            note=note,
            to_account=fm_to_account,
            transfer_pair_id=transfer_pair_id if type_ == "transfer" else None,
        )
        body = build_body(
            type_=this_type,
            date_=date_,
            amount=amount,
            currency=currency,
            category=category,
            account=fm_account,
            note=note,
            to_account=fm_to_account,
        )

        content = fm + "\n\n" + body + "\n"

        if not dry_run:
            full_path = os.path.join(vault_root, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            written_paths.append(rel_path)
        else:
            written_paths.append(rel_path + " (dry-run)")

    result = {
        "ok": True,
        "file_path": written_paths[0] if len(written_paths) == 1 else written_paths,
        "account": final_account,
        "source": source,
        "ask_message": ask_message,
    }
    if type_ == "transfer":
        result["transfer_pair_id"] = transfer_pair_id
        result["from_account"] = final_account
        result["to_account"] = to_account_final
    return result


def main():
    parser = argparse.ArgumentParser(description="创建交易记录 (Agent 入口)")
    parser.add_argument("--vault", required=True, help="vault 根目录")
    parser.add_argument("--type", required=True, choices=["expense", "income", "transfer"])
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--amount", required=True, type=float)
    parser.add_argument("--currency", default="CNY")
    parser.add_argument("--category", default="Other")
    parser.add_argument("--note", default="")
    parser.add_argument("--account", default=None, help="可选: 用户已指定账户")
    parser.add_argument("--to-account", default=None, help="仅 transfer")
    parser.add_argument("--transfer-pair-id", default=None, help="仅 transfer")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = create_transaction(
        vault_root=args.vault,
        type_=args.type,
        date_=args.date,
        amount=args.amount,
        currency=args.currency,
        category=args.category,
        note=args.note,
        account=args.account,
        to_account=args.to_account,
        transfer_pair_id=args.transfer_pair_id,
        config_path=args.config,
        dry_run=args.dry_run,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
