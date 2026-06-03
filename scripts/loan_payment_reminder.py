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
from datetime import date
from typing import Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import (
    find_transaction_files,
    parse_accounts,
    parse_frontmatter,
    file_status,
)
from lib.notifier import notify


def count_paid_periods(account: str, vault_root: str) -> int:
    """
    扫 Transactions/expenses/ 里 account=指定贷款账户 的笔数。
    简化: 假设每笔 expense = 1 期月供 (与 validate_transaction 的逻辑一致)。

    返回: 已还期数
    """
    count = 0
    for fp in find_transaction_files(vault_root):
        if file_status(fp) != "ACTIVE":
            continue
        # 只看 expense, 不看 transfer (transfer 是钱从一个账户到另一个, 不算还款)
        if "/transfers/" in fp:
            continue
        fm, _ = parse_frontmatter(fp)
        if not fm:
            continue
        if fm.get("type") != "expense":
            continue
        if fm.get("account") != account:
            continue
        count += 1
    return count


def check_consistency(acc_name: str, paid: int, remaining: Optional[int], total: int) -> Optional[str]:
    """
    校验 已还期数 + 剩余期数 == 总期数。

    返回: None (一致) 或 错误消息字符串
    """
    if remaining is None:
        return None  # 用户没填剩余, 没法校验
    if paid + remaining != total:
        return (
            f"数据不一致: 已还 {paid} 期 + 剩余 {remaining} 期 = {paid + remaining}, "
            f"但合同总期数 = {total} (差 {total - paid - remaining} 期)"
        )
    return None


def check_loans(vault_root: str, warn_days: int = 5) -> list:
    """
    扫描所有 loan 账户, 检查月供状态。

    核心算法 (V1.1.5):
    1. 字段: 起始月 + 月供日 + 合同总期数 + 月供金额 (4 个必填) + 剩余期数 (可选, 用于校验)
    2. 已还期数 = 扫 Transactions/expenses/ 里 account=贷款账户 的笔数
    3. 一致性校验: 已还期数 + 剩余期数 == 合同总期数 (可选, 缺剩余期数不校验)
    4. 下次月供日 = 起始月 + N 期 (N 是首个 >= 已还期数 的下一个月, 因为已还过的就不该再提醒)
       实际日 = min(月供日, 当月天数) — 2 月自动 28/29
    5. 合同结束月 = 起始月 + 总期数 - 1, 之后不提醒

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
        remaining = acc.get("remaining_months")  # 可选, 用于校验
        start = acc.get("start_month")
        payment_day = acc.get("payment_day")
        total = acc.get("total_months")

        # 必填字段检查
        missing = []
        if principal is None:
            missing.append("贷款总额")
        if monthly is None:
            missing.append("月供")
        if not start:
            missing.append("起始月")
        if payment_day is None:
            missing.append("月供日")
        if total is None:
            missing.append("合同总期数")
        if missing:
            errors.append((
                "INFO",
                f"贷款账户 {acc_name} 字段缺失: {', '.join(missing)}, "
                f"无法计算月供提醒时间",
            ))
            continue

        # 计算已还期数
        paid_periods = count_paid_periods(acc_name, vault_root)

        # 一致性校验: 只有 total 已知且 remaining 已知时才跑
        # (如果 total 没填, 没法校验, 跳过)
        if remaining is not None and total is not None:
            err = check_consistency(acc_name, paid_periods, remaining, total)
            if err:
                errors.append(("WARN", f"🏦 贷款 {acc_name}: {err}"))

        # 算"下次月供" = 第 (paid_periods + 1) 期
        # 起始月 = 第 1 期, 第 N 期 = 起始月 + (N-1) 个月
        target_period = paid_periods + 1
        from calendar import monthrange as _mr
        try:
            sy, sm = map(int, str(start).split("-"))
        except (ValueError, AttributeError):
            errors.append(("WARN", f"贷款账户 {acc_name} 起始月格式错误: {start}"))
            continue

        # 第 target_period 期的 (年, 月)
        target_total_months = sy * 12 + sm + (target_period - 1)
        target_year = target_total_months // 12
        target_month = target_total_months % 12
        if target_month == 0:
            target_month = 12
            target_year -= 1

        # 实际日 = min(payment_day, 当月天数)
        last_day = _mr(target_year, target_month)[1]
        actual_day = min(payment_day, last_day)
        next_due = date(target_year, target_month, actual_day)

        # 检查是否超过合同结束月
        # 注意: 这里用 target_period > total 判断, 而不是 target_total_months > end_total_months
        # 原因: target_period = paid_periods + 1, paid_periods=0 时 target_period=1, 永远不超期
        # 真正"应已结清"是 paid_periods >= total (已还完)
        if total is not None and paid_periods >= total:
            # 算结束月信息
            end_total_months = sy * 12 + sm + total - 1
            end_year = end_total_months // 12
            end_month_calc = end_total_months % 12
            if end_month_calc == 0:
                end_month_calc = 12
                end_year -= 1
            errors.append((
                "INFO",
                f"🏦 贷款 {acc_name} 应已结清 (合同 {total} 期, 已还 {paid_periods} 期, "
                f"结束月 {end_year}-{end_month_calc:02d}), 请检查账户表和交易记录",
            ))
            continue

        # ⚠️ 关键: 如果从未记过月供 (paid_periods == 0), 不要报"严重逾期"
        # 改报 INFO: "未启用月供记账, 如已开始还款请记 expense"
        if paid_periods == 0:
            total_info = f"{total} 期" if total is not None else "总期数未填"
            errors.append((
                "INFO",
                f"🏦 贷款 {acc_name} 未启用月供记账 ({total_info}, 起始 {start}, "
                f"月供 {monthly:.2f} {acc.get('currency','CNY')}). "
                f"如已实际开始还款, 请记一条 expense (account={acc_name}, amount={monthly:.2f})",
            ))
            continue

        gap = (next_due - today).days

        # 当月是否已还 (第 N 期正好是当月, 且 paid_periods == N-1 意味着还没还)
        already_paid_this_period = (paid_periods >= target_period)

        if gap < 0:
            # 月供日已是过去 (说明漏还了)
            overdue = -gap
            if already_paid_this_period:
                errors.append((
                    "INFO",
                    f"🏦 贷款 {acc_name} 第 {target_period} 期已还 ({monthly:.2f} {acc.get('currency','CNY')})",
                ))
            elif overdue <= 3:
                errors.append((
                    "ERROR",
                    f"🏦 贷款 {acc_name} 第 {target_period} 期 {next_due} 已过 {overdue} 天未还! "
                    f"({monthly:.2f} {acc.get('currency','CNY')})",
                ))
            else:
                errors.append((
                    "ERROR",
                    f"🏦 贷款 {acc_name} 第 {target_period} 期 {next_due} 已过 {overdue} 天严重逾期! "
                    f"({monthly:.2f} {acc.get('currency','CNY')})",
                ))
        elif gap <= warn_days:
            # 临近 (0~5 天)
            if already_paid_this_period:
                errors.append((
                    "INFO",
                    f"🏦 贷款 {acc_name} 第 {target_period} 期已还, 合同进度 {paid_periods}/{total}",
                ))
            else:
                errors.append((
                    "WARN",
                    f"🏦 贷款 {acc_name} 第 {target_period} 期 {next_due} 临近 (还有 {gap} 天), "
                    f"金额 {monthly:.2f} {acc.get('currency','CNY')}, "
                    f"已还 {paid_periods}/{total} 期",
                ))
        else:
            # 远期 (>5 天)
            errors.append((
                "INFO",
                f"🏦 贷款 {acc_name} 第 {target_period} 期 {next_due} (还有 {gap} 天), "
                f"金额 {monthly:.2f} {acc.get('currency','CNY')}, "
                f"已还 {paid_periods}/{total} 期",
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
