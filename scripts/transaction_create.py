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

    # 3. 解析默认账户
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

    # 4. 特殊: transfer 类型必须显式 from/to
    if type_ == "transfer":
        if not account or not to_account:
            return {
                "ok": False,
                "ask_message": "转账必须显式提供 from_account (--account) 和 to_account (--to-account)",
            }

    # 5. learning 冲突检查 (仅当 account 是自动解析的, 不是用户显式指定)
    ask_message = None
    if source in ("config", "learning", "fallback", "note") and final_account:
        conflict, _learning_after = record_usage(
            store_path=store_path,
            category=category,
            note=note,
            account=final_account,
        )
        if conflict:
            ask_message = conflict

    if not final_account:
        return {
            "ok": False,
            "ask_message": resolved.get("ask_message", "无法确定账户, 请用户指定"),
        }

    # 6. 决定文件路径
    if type_ == "expense":
        subdir = "Transactions/expenses"
    elif type_ == "income":
        subdir = "Transactions/incomes"
    elif type_ == "transfer":
        direction = "out" if not to_account or account != to_account else "in"
        # 默认: out (Agent 应该成对创建 out+in)
        subdir = f"Transactions/transfers/{direction}"
    else:
        return {"ok": False, "ask_message": f"未知 type: {type_}"}

    description = note or category or "tx"
    filename = generate_filename(type_, date_, description, amount, currency)
    rel_path = os.path.join(subdir, filename)
    full_path = os.path.join(vault_root, rel_path)

    if os.path.exists(full_path):
        return {
            "ok": False,
            "ask_message": f"文件已存在: {rel_path} (避免覆盖)",
        }

    # 7. 生成内容
    fm = build_frontmatter(
        type_=type_,
        date_=date_,
        amount=amount,
        currency=currency,
        category=category,
        account=final_account,
        note=note,
        to_account=to_account,
        transfer_pair_id=transfer_pair_id,
    )
    body = build_body(
        type_=type_,
        date_=date_,
        amount=amount,
        currency=currency,
        category=category,
        account=final_account,
        note=note,
        to_account=to_account,
    )

    content = fm + "\n\n" + body + "\n"

    # 8. 写文件
    if not dry_run:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    return {
        "ok": True,
        "file_path": rel_path,
        "account": final_account,
        "source": source,
        "ask_message": ask_message,
    }


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
