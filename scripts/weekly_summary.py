#!/usr/bin/env python3
"""
weekly_summary.py - 每周复盘 (#35)

用法:
    python3 weekly_summary.py [--vault <vault_root>]

输出内容:
    - 本周 (周一 00:00 ~ 周日 23:59) 交易笔数 / 总支出 / 总收入
    - 分类前 3 (餐饮 / 交通 / 购物 等)
    - 账户余额变化 (vs 上周末)
    - vs 上周对比 (同比 +/- %)
    - 写到 alerts.md (Agent 周日 20:00 定时跑, 推送给用户)
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import date, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import find_transaction_files, parse_frontmatter, parse_accounts, file_status
from lib.balance import compute_balances
from lib.notifier import notify


def week_range(today: date) -> tuple:
    """返回 (本周一日期, 本周日日期)。"""
    week_start = today - timedelta(days=today.weekday())  # 周一
    week_end = week_start + timedelta(days=6)  # 周日
    return week_start, week_end


def collect_period(vault_root: str, start: date, end: date) -> dict:
    """
    收集 [start, end] 内的交易。
    返回:
      {
        "tx_count": int,
        "total_expense": float (per currency dict),
        "total_income": float (per currency dict),
        "by_category": {"餐饮": 150.0, ...} (per currency dict),
        "by_account": {account: net_change} (per currency dict),
      }
    """
    out = {
        "tx_count": 0,
        "total_expense": defaultdict(float),
        "total_income": defaultdict(float),
        "by_category": defaultdict(lambda: defaultdict(float)),
        "by_account": defaultdict(lambda: defaultdict(float)),
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
            acc = fm.get("account")
            if acc:
                out["by_account"][acc][ccy] -= amount
        elif tx_type == "income":
            out["total_income"][ccy] += amount
            acc = fm.get("account")
            if acc:
                out["by_account"][acc][ccy] += amount
        elif tx_type == "transfer":
            if "/transfers/out/" in filepath:
                acc = fm.get("from_account")
                if acc:
                    out["by_account"][acc][ccy] -= amount
            elif "/transfers/in/" in filepath:
                acc = fm.get("to_account")
                if acc:
                    out["by_account"][acc][ccy] += amount

    return out


def fmt_money(d: dict) -> str:
    return ", ".join(f"{ccy} {amt:.2f}" for ccy, amt in d.items())


def build_summary(vault_root: str) -> str:
    today = date.today()
    this_start, this_end = week_range(today)
    last_start = this_start - timedelta(days=7)
    last_end = this_start - timedelta(days=1)

    this_week = collect_period(vault_root, this_start, this_end)
    last_week = collect_period(vault_root, last_start, last_end)

    lines = []
    lines.append(f"📅 每周复盘 ({this_start} ~ {this_end})")
    lines.append("")

    # 1. 笔数 + 收支
    lines.append(f"📊 交易笔数: {this_week['tx_count']} 笔 (上周 {last_week['tx_count']} 笔)")
    if this_week["total_expense"] or this_week["total_income"]:
        lines.append(f"💸 总支出: {fmt_money(this_week['total_expense'])}")
        lines.append(f"💰 总收入: {fmt_money(this_week['total_income'])}")
        # 同比
        for ccy in set(list(this_week["total_expense"].keys()) + list(last_week["total_expense"].keys())):
            t = this_week["total_expense"].get(ccy, 0)
            l = last_week["total_expense"].get(ccy, 0)
            if l > 0:
                pct = (t - l) / l * 100
                arrow = "📈" if pct > 0 else "📉"
                lines.append(f"  {arrow} vs 上周: {ccy} 支出 {pct:+.1f}%")
    else:
        lines.append("(本周暂无交易)")
    lines.append("")

    # 2. 分类 top 3 (per currency)
    if this_week["by_category"]:
        lines.append("🏷️ 分类 Top 3 (支出):")
        for ccy, cats in this_week["by_category"].items():
            top = sorted(cats.items(), key=lambda x: -x[1])[:3]
            for cat, amt in top:
                lines.append(f"  {ccy} {cat}: {amt:.2f}")
        lines.append("")

    # 3. 账户余额 (截止今天)
    balances = compute_balances(vault_root)
    if balances:
        lines.append("🏦 账户余额 (截止今天):")
        for (acc, ccy), bal in sorted(balances.items()):
            lines.append(f"  {acc} ({ccy}): {bal:.2f}")
        lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="每周财务复盘 (#35)")
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
    summary = build_summary(vault)
    print(summary)

    if not args.no_notify:
        notify(
            vault_root=vault,
            title="📅 每周复盘",
            body=summary,
            severity="INFO",
            details=[summary],
            source="weekly_summary.py",
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
