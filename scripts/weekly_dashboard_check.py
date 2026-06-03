#!/usr/bin/env python3
"""
weekly_dashboard_check.py - 周度检查: Python 计算 vs Dataview 仪表盘

用法:
    python3 weekly_dashboard_check.py [--vault <vault_root>]

DataviewJS 在 finance-dashboard.md 里计算的余额, 必须和 Python 算的一致。
由于 Dataview 只能"展示", 这个脚本的实际意义是:
  1. 跑 Python 算出权威余额
  2. 检查仪表盘里的 DataviewJS 代码块是否引用了正确的源文件
  3. 检查账户表是否完整
  4. 提示用户"对账时这个数字应该匹配"

不直接读 Dataview 渲染结果 (跨平台做不到), 而是检查:
  - 仪表盘里是否引用了所有账户类型
  - DataviewJS 代码块的字段名是否和项目规范一致
  - 是否有 Dataview 模板中常见的笔误
"""

import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import parse_accounts, find_transaction_files, parse_frontmatter
from lib.balance import compute_balances
from lib.notifier import notify


def check_dashboard_references(vault_root: str) -> list:
    """
    检查 Dashboards/finance-dashboard.md 的内容。
    """
    errors = []
    dash_path = os.path.join(vault_root, "Dashboards", "finance-dashboard.md")
    if not os.path.isfile(dash_path):
        return [("ERROR", f"仪表盘文件不存在: {dash_path}")]

    with open(dash_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 关键检查项
    checks = {
        "expenses 目录引用": r'["\']\${vault[^}]*}["\']|\bexpenses\b',
        "incomes 目录引用": r'["\']\${vault[^}]*}["\']|\bincomes\b',
        "transfers/out 引用": r'transfers[/\\]out',
        "transfers/in 引用": r'transfers[/\\]in',
        "transfer_pair_id 字段引用": r'transfer_pair_id',
        # 余额块: 现在是 dataview 读 balances.md 快照,不再是 dataviewjs 自算
        # 改成检查 balances.md 引用,更准确
        "余额快照引用": r'balances\.md|type\s*=\s*["\']balance-snapshot["\']',
    }
    for name, pattern in checks.items():
        if not re.search(pattern, content):
            errors.append(("WARN", f"仪表盘缺少: {name}"))

    # 关键字段名
    expected_fields = ["amount", "currency", "type", "account", "from_account", "to_account", "transfer_pair_id"]
    for field in expected_fields:
        if field not in content:
            errors.append(("WARN", f"仪表盘未引用字段: {field}"))

    return errors


def check_accounts_table_complete(vault_root: str) -> list:
    """
    检查账户表是否完整, 且初始余额都有。
    """
    errors = []
    accounts = parse_accounts(vault_root)
    if not accounts:
        return [("ERROR", "account-list.md 解析失败或为空 (账户数为 0)")]

    for name, info in accounts.items():
        if not info.get("currency"):
            errors.append(("WARN", f"账户 '{name}' 缺少 currency 字段"))
        if info.get("initial_balance") is None:
            errors.append(("WARN", f"账户 '{name}' 缺少 initial_balance 字段"))

    return errors


def print_authoritative_balances(vault_root: str) -> None:
    """
    打印 Python 算出的权威余额, 供用户对账 Dataview 显示。
    """
    balances = compute_balances(vault_root)
    if not balances:
        print("(无账户数据)")
        return

    print("\n📊 权威余额 (Python 计算) — 仪表盘 `Accounts/balances.md` 快照显示应与此一致:")
    print(f"  {'账户':<20} {'币种':<6} {'余额':>15}")
    print(f"  {'-' * 20} {'-' * 6} {'-' * 15}")
    for (acc, ccy), bal in sorted(balances.items()):
        print(f"  {acc:<20} {ccy:<6} {bal:>15.2f}")


def main():
    ap = argparse.ArgumentParser(description="周度对账: Dataview 仪表盘 vs Python")
    ap.add_argument(
        "--vault",
        default=os.path.expanduser("~/Obsidian/finance"),
        help="vault 根目录",
    )
    ap.add_argument(
        "--no-notify",
        action="store_true",
    )
    args = ap.parse_args()

    vault = os.path.abspath(os.path.expanduser(args.vault))

    print("🔍 检查仪表盘文件结构...")
    errors = check_dashboard_references(vault)
    print("🔍 检查账户表完整性...")
    errors += check_accounts_table_complete(vault)

    if not errors:
        print("✅ 仪表盘和账户表结构检查通过\n")
    else:
        print(f"\n⚠️  发现 {len(errors)} 个结构问题:")
        for level, msg in errors:
            print(f"  [{level}] {msg}")

    print_authoritative_balances(vault)

    if errors and not args.no_notify:
        details = [f"{level}: {msg}" for level, msg in errors]
        notify(
            vault_root=vault,
            title="周度对账结构告警",
            body=f"发现 {len(errors)} 个结构问题",
            severity="WARN",
            details=details,
            source="weekly_dashboard_check.py",
        )

    # 周度检查是软告警, 永远不退出非 0 (结构问题不致命)
    sys.exit(0)


if __name__ == "__main__":
    main()
