#!/usr/bin/env python3
"""
validate_transaction.py - 单笔交易校验

用法:
    python3 validate_transaction.py <transaction_file_path> [--vault <vault_root>]

退出码:
    0 - 校验通过
    1 - 校验失败 (有 error 级别问题)
    2 - 文件找不到 / 参数错误

校验内容:
    1. 必填字段齐全
    2. amount > 0
    3. 日期合法 (YYYY-MM-DD)
    4. 币种合法
    5. 账户名在 account-list.md 注册
    6. (transfer) transfer_pair_id 在配对文件中能找到
    7. (transfer) out 和 in 文件的 amount/currency 完全一致
    8. (transfer) from_account != to_account
"""

import argparse
import os
import re
import sys
from pathlib import Path

# 让脚本能 import lib
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import (
    parse_frontmatter,
    find_accounts_file,
    parse_accounts,
    find_transfer_pair,
    find_transaction_files,
)
from lib.notifier import notify


REQUIRED_FIELDS = ["type", "date", "amount", "currency", "status"]
VALID_CURRENCIES = {"CNY", "USD", "EUR", "HKD", "JPY", "GBP"}
VALID_TYPES = {"expense", "income", "transfer"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate(filepath: str, vault_root: str) -> list:
    """
    返回 errors 列表 (空列表 = 通过)。
    每条 error 是 (level, message) — level: 'ERROR' | 'WARN'
    """
    errors = []

    if not os.path.isfile(filepath):
        return [("ERROR", f"文件不存在: {filepath}")]

    fm, _ = parse_frontmatter(filepath)
    if not fm:
        return [("ERROR", "无法解析 frontmatter (文件无 YAML 头部或格式错误)")]

    # 1. 必填字段
    for field in REQUIRED_FIELDS:
        if field not in fm or fm[field] in (None, ""):
            errors.append(("ERROR", f"必填字段缺失: {field}"))

    if errors:
        return errors  # 必填缺失时不再深入校验

    # 2. amount > 0
    amount = fm.get("amount")
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            errors.append(("ERROR", f"amount 必须 > 0 (当前: {amount})"))
    except (TypeError, ValueError):
        errors.append(("ERROR", f"amount 不是数字: {amount}"))

    # 3. 日期
    date = fm.get("date")
    if not isinstance(date, str) or not DATE_RE.match(date):
        errors.append(("ERROR", f"date 格式错误 (期望 YYYY-MM-DD): {date}"))

    # 4. 币种
    currency = fm.get("currency")
    if currency not in VALID_CURRENCIES:
        errors.append(("WARN", f"币种不在推荐列表: {currency} (推荐: {', '.join(sorted(VALID_CURRENCIES))})"))

    # 5. type
    tx_type = fm.get("type")
    if tx_type not in VALID_TYPES:
        errors.append(("ERROR", f"type 非法: {tx_type} (期望: {', '.join(VALID_TYPES)})"))
        return errors  # 后续 type-specific 校验没意义

    # 6. 账户名校验
    accounts = parse_accounts(vault_root)
    registered = set(accounts.keys())

    if tx_type in ("expense", "income"):
        account = fm.get("account")
        if not account:
            errors.append(("ERROR", "expense/income 必须有 account 字段"))
        elif account not in registered:
            errors.append(("WARN", f"账户 '{account}' 未在 account-list.md 注册 (拼写错误? 或需添加)"))

    elif tx_type == "transfer":
        from_acc = fm.get("from_account")
        to_acc = fm.get("to_account")
        pair_id = fm.get("transfer_pair_id")

        if not from_acc or not to_acc:
            errors.append(("ERROR", "transfer 必须有 from_account 和 to_account"))
        elif from_acc == to_acc:
            errors.append(("ERROR", f"transfer 双方账户相同: {from_acc}"))

        if from_acc and from_acc not in registered:
            errors.append(("WARN", f"转出账户 '{from_acc}' 未在 account-list.md 注册"))
        if to_acc and to_acc not in registered:
            errors.append(("WARN", f"转入账户 '{to_acc}' 未在 account-list.md 注册"))

        if not pair_id:
            errors.append(("ERROR", "transfer 必须有 transfer_pair_id"))
        else:
            # 7. 找配对
            direction = "out" if "/transfers/out/" in filepath else (
                "in" if "/transfers/in/" in filepath else None
            )
            pair_files = find_transfer_pair(vault_root, pair_id, direction=None)

            if direction is None:
                errors.append(("WARN", f"文件不在 transfers/out/ 或 transfers/in/ 目录下: {filepath}"))

            # 当前文件不应算在内
            other_files = [f for f in pair_files if os.path.abspath(f) != os.path.abspath(filepath)]

            if not other_files:
                errors.append(("ERROR", f"transfer_pair_id '{pair_id}' 找不到配对文件 (期望另一端也用相同 ID)"))
            else:
                # 8. 配对字段一致
                for pf in other_files:
                    pfm, _ = parse_frontmatter(pf)
                    if float(pfm.get("amount", 0)) != float(amount):
                        errors.append(
                            ("ERROR", f"配对文件 amount 不一致: {os.path.basename(pf)} 有 {pfm.get('amount')}, 当前有 {amount}")
                        )
                    if pfm.get("currency") != currency:
                        errors.append(
                            ("ERROR", f"配对文件 currency 不一致: {os.path.basename(pf)} 有 {pfm.get('currency')}, 当前有 {currency}")
                        )
                    # from/to 必须完全一致 (out 和 in 表达同一笔交易, 语义统一)
                    if from_acc != pfm.get("from_account") or to_acc != pfm.get("to_account"):
                        errors.append(
                            ("ERROR", f"配对文件账户不一致: {os.path.basename(pf)} 是 {pfm.get('from_account')}→{pfm.get('to_account')}, 当前是 {from_acc}→{to_acc}")
                        )

    return errors


def main():
    ap = argparse.ArgumentParser(description="校验单笔交易文件")
    ap.add_argument("filepath", help="要校验的 .md 文件路径")
    ap.add_argument(
        "--vault",
        default=os.path.expanduser("~/Obsidian/finance"),
        help="vault 根目录 (默认: ~/Obsidian/finance)",
    )
    ap.add_argument(
        "--no-notify",
        action="store_true",
        help="不写 alerts.md 和不发送通知 (dry-run 模式)",
    )
    args = ap.parse_args()

    vault = os.path.abspath(os.path.expanduser(args.vault))
    filepath = os.path.abspath(args.filepath)

    if not os.path.isfile(filepath):
        print(f"❌ 错误: 文件不存在: {filepath}", file=sys.stderr)
        sys.exit(2)

    errors = validate(filepath, vault)

    if not errors:
        print(f"✅ 校验通过: {os.path.basename(filepath)}")
        sys.exit(0)

    # 有问题
    has_error = any(level == "ERROR" for level, _ in errors)
    severity = "ERROR" if has_error else "WARN"

    print(f"{'❌' if has_error else '⚠️'}  校验{'失败' if has_error else '告警'}: {os.path.basename(filepath)}")
    for level, msg in errors:
        marker = "  ❌" if level == "ERROR" else "  ⚠️ "
        print(f"{marker} [{level}] {msg}")

    # 软告警: 写 alerts.md + 桌面通知 (除非 --no-notify)
    if not args.no_notify:
        title = f"财务单笔校验{'失败' if has_error else '告警'}"
        details = [f"{level}: {msg}" for level, msg in errors]
        notify(
            vault_root=vault,
            title=title,
            body=f"{os.path.basename(filepath)}: {len(errors)} 个问题",
            severity=severity,
            details=details,
            source="validate_transaction.py",
        )

    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
