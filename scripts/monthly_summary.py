#!/usr/bin/env python3
"""
monthly_summary.py - 月末自检 (#36)

用法:
    python3 monthly_summary.py [--vault <vault_root>] [--month YYYY-MM]

输出内容:
    - 本月 (1 号 ~ 当天) 交易笔数 / 总支出 / 总收入
    - 储蓄率 = (收入 - 支出) / 收入
    - 分类汇总 (全部)
    - 跨账户流量 (转出/转入 总额)
    - 写到 alerts.md

默认跑当月。--month 可指定历史月 (YYYY-MM)。
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import find_transaction_files, parse_frontmatter, parse_accounts, file_status
from lib.balance import compute_balances
from lib.notifier import notify


def month_range(year: int, month: int) -> tuple:
    """返回 (本月 1 号, 本月最后一天)。"""
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - __import__("datetime").timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - __import__("datetime").timedelta(days=1)
    return start, end


def collect_period(vault_root: str, start: date, end: date) -> dict:
    out = {
        "tx_count": 0,
        "total_expense": defaultdict(float),
        "total_income": defaultdict(float),
        "by_category": defaultdict(lambda: defaultdict(float)),
        "transfer_in_total": defaultdict(float),
        "transfer_out_total": defaultdict(float),
    }
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
        if d < start or d > end:
            continue

        ccy = fm.get("currency", "CNY")
        amount = float(fm.get("amount", 0) or 0)
        if amount <= 0:
            continue

        out["tx_count"] += 1
        tx_type = fm.get("type")

        if tx_type == "expense":
            out["total_expense"][ccy] += amount
            cat = fm.get("category", "其他")
            out["by_category"][ccy][cat] += amount
        elif tx_type == "income":
            out["total_income"][ccy] += amount
        elif tx_type == "transfer":
            if "/transfers/out/" in filepath:
                out["transfer_out_total"][ccy] += amount
            elif "/transfers/in/" in filepath:
                out["transfer_in_total"][ccy] += amount
    return out


def fmt_money(d: dict) -> str:
    return ", ".join(f"{ccy} {amt:.2f}" for ccy, amt in d.items())


def build_summary(vault_root: str, year: int, month: int) -> str:
    start, end = month_range(year, month)
    period = collect_period(vault_root, start, end)

    lines = []
    lines.append(f"📅 月度总结 ({year}-{month:02d}: {start} ~ {end})")
    lines.append("")

    # 1. 笔数
    lines.append(f"📊 交易笔数: {period['tx_count']} 笔")
    lines.append("")

    # 2. 收支 + 储蓄率
    if period["total_expense"] or period["total_income"]:
        lines.append(f"💸 总支出: {fmt_money(period['total_expense'])}")
        lines.append(f"💰 总收入: {fmt_money(period['total_income'])}")
        for ccy in set(list(period["total_expense"].keys()) + list(period["total_income"].keys())):
            inc = period["total_income"].get(ccy, 0)
            exp = period["total_expense"].get(ccy, 0)
            if inc > 0:
                rate = (inc - exp) / inc * 100
                bar = "🟢" if rate >= 30 else "🟡" if rate >= 10 else "🔴"
                lines.append(f"  {bar} {ccy} 储蓄率: {rate:.1f}% (目标 ≥ 30%)")
            else:
                if exp > 0:
                    lines.append(f"  🔴 {ccy} 储蓄率: N/A (有支出无收入)")
        lines.append("")

    # 3. 分类汇总
    if period["by_category"]:
        lines.append("🏷️ 分类汇总 (支出):")
        for ccy, cats in period["by_category"].items():
            for cat, amt in sorted(cats.items(), key=lambda x: -x[1]):
                lines.append(f"  {ccy} {cat}: {amt:.2f}")
        lines.append("")

    # 4. 跨账户流量
    if period["transfer_out_total"] or period["transfer_in_total"]:
        lines.append("🔄 跨账户流量:")
        for ccy in set(list(period["transfer_out_total"].keys()) + list(period["transfer_in_total"].keys())):
            tout = period["transfer_out_total"].get(ccy, 0)
            tin = period["transfer_in_total"].get(ccy, 0)
            lines.append(f"  {ccy}: 转出 {tout:.2f} / 转入 {tin:.2f}")
        lines.append("")

    # 5. 账户余额
    balances = compute_balances(vault_root)
    if balances:
        lines.append("🏦 账户余额 (截止月底):")
        for (acc, ccy), bal in sorted(balances.items()):
            lines.append(f"  {acc} ({ccy}): {bal:.2f}")
        lines.append("")

    if period["tx_count"] == 0:
        lines.append("(本月暂无交易)")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="每月财务总结 (#36)")
    ap.add_argument(
        "--vault",
        default=os.path.expanduser("~/Obsidian/finance"),
        help="vault 根目录",
    )
    ap.add_argument(
        "--month",
        default=None,
        help="YYYY-MM 格式, 默认当月",
    )
    ap.add_argument(
        "--no-notify",
        action="store_true",
        help="不写 alerts.md 和不发送通知",
    )
    args = ap.parse_args()

    vault = os.path.abspath(os.path.expanduser(args.vault))

    if args.month:
        try:
            y, m = args.month.split("-")
            year, month = int(y), int(m)
        except ValueError:
            print(f"❌ --month 格式错误: {args.month} (应为 YYYY-MM)", file=sys.stderr)
            sys.exit(1)
    else:
        today = date.today()
        year, month = today.year, today.month

    summary = build_summary(vault, year, month)
    print(summary)

    if not args.no_notify:
        notify(
            vault_root=vault,
            title=f"📅 {year}-{month:02d} 月度总结",
            body=summary,
            severity="INFO",
            details=[summary],
            source="monthly_summary.py",
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
