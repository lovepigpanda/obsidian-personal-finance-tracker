#!/usr/bin/env python3
"""
loan_payment_reminder.py - 贷款月供提醒 (#37 贷款账户)

用法:
    python3 loan_payment_reminder.py [--vault <vault_root>]

逻辑:
    1. 从 account-list.md 找所有 type=loan 的账户
    2. 取每笔贷款的"起始月 start_month" + "月供 monthly_payment" + "剩余期数 remaining_months"
    3. 计算下一次月供日 (起始月对应日, 之后每月同一天)
    4. 距月供日 <= 5 天: WARN (提醒)
    5. 月供日已过 0~3 天: ERROR (逾期未记账)
    6. 月供日已过 4+ 天: ERROR (严重逾期, 一定出问题了)
    7. 当月未记账: WARN (该月还没还)

数据约定:
    - 贷款账户余额 = -未还本金 (负数)
    - 还月供 = 一条 expense 交易, account=贷款账户, amount=月供
    - 不需要单独 tracking: 直接靠交易文件自动计算余额, 跟信用卡一样

注意: 本脚本不校验"已还多少"对不对, 只提醒"该还了"+"逾期没记账"。
"""

import argparse
import os
import sys
from calendar import monthrange
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import (
    find_transaction_files,
    parse_accounts,
    parse_frontmatter,
    file_status,
)
from lib.notifier import notify


def next_payment_date(start_month: str, today: date) -> date:
    """
    给定起始月 (YYYY-MM), 计算下一次月供日 (用起始月最后一天作为基准日)。

    简化处理: 起始月是 "2024-03" → 第一次月供 2024-03 的某一天 (用月末)。
    之后每月同日。如果起始日是 31, 而 2 月只有 28 天, 用当月最后一天。

    参数:
        start_month: "YYYY-MM" 格式
        today: 当前日期

    返回:
        下一次月供应到日期
    """
    year, month = map(int, start_month.split("-"))

    # 起始月的月供日 = 起始月最后一天 (简化处理, 用户可在账户表里微调)
    start_day = monthrange(year, month)[1]

    # 找今天之后的下一个月供日
    payment_year, payment_month = year, month
    while True:
        try:
            candidate = date(payment_year, payment_month, start_day)
        except ValueError:
            # 起始日超过当月天数 (如 31 在 2 月)
            last_day = monthrange(payment_year, payment_month)[1]
            candidate = date(payment_year, payment_month, last_day)

        if candidate >= today:
            return candidate

        # 下一月
        payment_month += 1
        if payment_month > 12:
            payment_month = 1
            payment_year += 1


def paid_this_month(account: str, today: date, vault_root: str) -> bool:
    """
    检查指定贷款账户在当月是否已有一笔月供记账 (expense with account=loan)。

    简化: 找当月所有 expense 中 account=指定贷款账户 的笔数 >= 1 即可。
    """
    files = find_transaction_files(vault_root)
    for fp in files:
        if file_status(fp) != "ACTIVE":
            continue
        fm, _ = parse_frontmatter(fp)
        if not fm:
            continue
        if fm.get("type") != "expense":
            continue
        if fm.get("account") != account:
            continue
        d_str = str(fm.get("date", ""))
        try:
            d = date.fromisoformat(d_str)
        except (ValueError, TypeError):
            continue
        if d.year == today.year and d.month == today.month:
            return True
    return False


def check_loans(vault_root: str, warn_days: int = 5) -> list:
    """
    扫描所有 loan 账户, 检查月供状态。

    返回: list of (level, message) tuples
    """
    errors = []
    accounts = parse_accounts(vault_root)
    today = date.today()

    for acc_name, acc in accounts.items():
        if acc.get("type") != "loan":
            continue

        principal = acc.get("principal")
        monthly = acc.get("monthly_payment")
        remaining = acc.get("remaining_months")
        start = acc.get("start_month")

        # 字段缺失: 给 INFO 提示, 不算错
        missing = []
        if principal is None:
            missing.append("贷款总额")
        if monthly is None:
            missing.append("月供")
        if remaining is None:
            missing.append("剩余期数")
        if not start:
            missing.append("起始月")
        if missing:
            errors.append((
                "INFO",
                f"贷款账户 {acc_name} 字段缺失: {', '.join(missing)}, "
                f"无法计算月供提醒时间",
            ))
            continue

        # 计算下一次月供日
        try:
            next_due = next_payment_date(str(start), today)
        except (ValueError, AttributeError) as e:
            errors.append((
                "WARN",
                f"贷款账户 {acc_name} 起始月格式错误: {start} ({e})",
            ))
            continue

        gap = (next_due - today).days

        # 当月是否已还
        paid = paid_this_month(acc_name, today, vault_root)

        if gap < 0:
            # 逾期 (next_due 已是过去)
            overdue = -gap
            if paid:
                # 已还, 没问题
                errors.append((
                    "INFO",
                    f"🏦 贷款 {acc_name} 本月月供已还 ({monthly:.2f} {acc.get('currency','CNY')}), "
                    f"下次月供 {next_due} (还有 {-gap + 30} 天左右)",
                ))
            elif overdue <= 3:
                errors.append((
                    "ERROR",
                    f"🏦 贷款 {acc_name} 月供 {next_due} 已过 {overdue} 天未还! "
                    f"({monthly:.2f} {acc.get('currency','CNY')})",
                ))
            else:
                errors.append((
                    "ERROR",
                    f"🏦 贷款 {acc_name} 月供 {next_due} 已过 {overdue} 天严重逾期! "
                    f"({monthly:.2f} {acc.get('currency','CNY')})",
                ))
        elif gap <= warn_days:
            # 临近 (0~5 天)
            if paid:
                errors.append((
                    "INFO",
                    f"🏦 贷款 {acc_name} 本月月供已还, "
                    f"下次月供 {next_due} (还有 {gap} 天)",
                ))
            else:
                errors.append((
                    "WARN",
                    f"🏦 贷款 {acc_name} 月供 {next_due} 临近 (还有 {gap} 天), "
                    f"金额 {monthly:.2f} {acc.get('currency','CNY')}, "
                    f"剩余 {remaining} 期",
                ))
        else:
            # 远期 (>5 天), 仅当月未还才提醒
            if paid:
                errors.append((
                    "INFO",
                    f"🏦 贷款 {acc_name} 本月月供已还, "
                    f"下次月供 {next_due} (还有 {gap} 天)",
                ))
            else:
                # 上月还了但本月还没还 (例如今天 6-5, 下次月供 6-25, 但 6 月还没记账)
                # 这种情况不强制 WARN, 仅 INFO
                errors.append((
                    "INFO",
                    f"🏦 贷款 {acc_name} 下次月供 {next_due} (还有 {gap} 天), "
                    f"金额 {monthly:.2f} {acc.get('currency','CNY')}, 剩余 {remaining} 期",
                ))

    return errors


def main():
    ap = argparse.ArgumentParser(description="贷款月供提醒 (#37)")
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
    errors = check_loans(vault)

    if not errors:
        print("✅ 无贷款月供提醒")
        if not args.no_notify:
            from lib.notifier import write_alert
            write_alert(
                vault,
                title="贷款月供检查通过",
                severity="INFO",
                details=["所有贷款账户月供状态正常"],
                source="loan_payment_reminder.py",
            )
        return

    # 分类
    actionable = [(l, m) for l, m in errors if l in ("ERROR", "WARN")]
    has_error = any(l == "ERROR" for l, _ in actionable)

    print(f"\n{'❌' if has_error else '⚠️ '}  发现 {len(actionable)} 个问题")
    for level, msg in actionable:
        marker = "  ❌" if level == "ERROR" else "  ⚠️ "
        print(f"{marker} [{level}] {msg}")
    for level, msg in errors:
        if level == "INFO":
            print(f"  ℹ️  [{level}] {msg}")

    if not args.no_notify:
        details = [f"[{level}] {msg}" for level, msg in errors]
        notify(
            vault_root=vault,
            title="贷款月供提醒",
            body=f"发现 {len(actionable)} 个问题" if actionable else "贷款状态正常",
            severity="ERROR" if has_error else ("WARN" if actionable else "INFO"),
            details=details,
            source="loan_payment_reminder.py",
        )

    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
