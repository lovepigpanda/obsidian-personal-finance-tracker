#!/usr/bin/env python3
"""
credit_card_reminder.py - 信用卡还款提醒 (#23)

用法:
    python3 credit_card_reminder.py [--vault <vault_root>]

逻辑:
    1. 从 account-list.md 找所有 type=credit-card 的账户
    2. 取每张卡的"账单日"+"还款日"
    3. 计算下一次出账日 (statement_day) 和还款日 (due_day)
    4. 如果还款日距今 <= 5 天, 报 WARN (提醒)
    5. 如果还款日已过, 报 ERROR (逾期)
    6. 写到 alerts.md
"""

import argparse
import os
import sys
from datetime import date, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import parse_accounts
from lib.balance import compute_balances
from lib.notifier import notify


def next_statement_and_due(statement_day: int, due_day: int, today: date) -> tuple:
    """
    给定账单日 (1-31) 和还款日 (1-31), 计算下一次出账日和对应还款日。

    假设出账日后 20 天内是还款日 (国内常见)。如果 due_day >= statement_day,
    还款日在出账当月；否则跨月 (出账日次月)。
    """
    # 找下一次出账日
    if today.day < statement_day:
        next_stmt = date(today.year, today.month, statement_day)
    else:
        # 跳到下月
        if today.month == 12:
            next_stmt = date(today.year + 1, 1, statement_day)
        else:
            next_stmt = date(today.year, today.month + 1, statement_day)

    # 找对应还款日
    if due_day >= statement_day:
        # 同月 (出账后 N 天)
        try:
            next_due = date(next_stmt.year, next_stmt.month, due_day)
        except ValueError:
            # due_day > 当月天数, 用当月最后一天
            from calendar import monthrange
            last_day = monthrange(next_stmt.year, next_stmt.month)[1]
            next_due = date(next_stmt.year, next_stmt.month, last_day)
    else:
        # 跨月 (出账后 N 天, N 跨月)
        if next_stmt.month == 12:
            try:
                next_due = date(next_stmt.year + 1, 1, due_day)
            except ValueError:
                next_due = date(next_stmt.year + 1, 1, 31)
        else:
            try:
                next_due = date(next_stmt.year, next_stmt.month + 1, due_day)
            except ValueError:
                from calendar import monthrange
                last_day = monthrange(next_stmt.year, next_stmt.month + 1)[1]
                next_due = date(next_stmt.year, next_stmt.month + 1, last_day)
    return next_stmt, next_due


def check_credit_cards(vault_root: str, warn_days: int = 5) -> list:
    """对每张信用卡: 计算下次还款日, < warn_days 报 WARN, < 0 报 ERROR。"""
    from calendar import monthrange

    errors = []
    accounts = parse_accounts(vault_root)
    if not accounts:
        return errors

    today = date.today()
    balances = compute_balances(vault_root)

    found_credit_card = False
    for name, info in accounts.items():
        if info.get("type") != "credit-card":
            continue
        found_credit_card = True
        stmt_day = info.get("statement_day")
        due_day = info.get("due_day")
        if not stmt_day or not due_day:
            errors.append((
                "WARN",
                f"信用卡 {name} 缺少账单日/还款日, 跳过提醒 (在 account-list.md 补全)"
            ))
            continue

        next_stmt, next_due = next_statement_and_due(stmt_day, due_day, today)
        gap = (next_due - today).days
        bal = balances.get((name, info["currency"]), 0.0)

        if gap < 0:
            errors.append((
                "ERROR",
                f"💳 信用卡 {name} 还款日已过 {abs(gap)} 天 ({next_due}), 当前余额 {bal:.2f} {info['currency']}, 立即处理!"
            ))
        elif gap <= warn_days:
            errors.append((
                "WARN",
                f"💳 信用卡 {name} 还款日 {next_due} (还有 {gap} 天), 当前余额 {bal:.2f} {info['currency']}"
            ))
        else:
            errors.append((
                "INFO",
                f"💳 信用卡 {name} 下次还款 {next_due} (还有 {gap} 天), 余额 {bal:.2f} {info['currency']}"
            ))

    if not found_credit_card:
        errors.append((
            "INFO",
            "账户列表中暂无信用卡账户 (type=credit-card), 如有请在 account-list.md 添加"
        ))
    return errors


def main():
    ap = argparse.ArgumentParser(description="信用卡还款提醒 (#23)")
    ap.add_argument(
        "--vault",
        default=os.path.expanduser("~/Obsidian/finance"),
        help="vault 根目录",
    )
    ap.add_argument(
        "--warn-days",
        type=int,
        default=5,
        help="还款日前 N 天提醒 (默认 5)",
    )
    ap.add_argument(
        "--no-notify",
        action="store_true",
        help="不写 alerts.md 和不发送通知",
    )
    args = ap.parse_args()

    vault = os.path.abspath(os.path.expanduser(args.vault))
    errors = check_credit_cards(vault, args.warn_days)

    if not errors:
        print("✅ 无信用卡提醒")
        sys.exit(0)

    has_error = any(l == "ERROR" for l, _ in errors)
    severity = "ERROR" if has_error else "WARN"

    for level, msg in errors:
        marker = "  ❌" if level == "ERROR" else "  ⚠️ " if level == "WARN" else "  ℹ️ "
        print(f"{marker} [{level}] {msg}")

    actionable = [(l, m) for l, m in errors if l in ("ERROR", "WARN")]
    if not args.no_notify and actionable:
        details = [f"[{l}] {m}" for l, m in errors]
        notify(
            vault_root=vault,
            title="💳 信用卡还款提醒",
            body=f"发现 {len(actionable)} 张卡需要处理",
            severity=severity,
            details=details,
            source="credit_card_reminder.py",
        )
    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
