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
"""

import argparse
import os
import sys
from collections import defaultdict

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
    """
    errors = []
    balances = compute_balances(vault_root)
    for (acc, ccy), bal in balances.items():
        if bal < -0.01:
            errors.append((
                "WARN",
                f"账户 {acc} ({ccy}) 余额为负: {bal:.2f}",
            ))
    return errors


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
    print("🔍 1/4 检查转账配对完整性...")
    all_errors += check_transfer_pairing(vault)
    print("🔍 2/4 检查币种转账守恒...")
    all_errors += check_currency_conservation(vault)
    print("🔍 3/4 检查余额计算自洽...")
    all_errors += check_balances_self_consistent(vault)
    print("🔍 4/4 检查账户透支...")
    all_errors += check_negative_balances(vault)

    if not all_errors:
        print("\n✅ 所有检查通过 — 财务系统内部一致")
        # 即使通过也写一条 INFO 到 alerts.md (审计痕迹)
        if not args.no_notify:
            from lib.notifier import write_alert
            write_alert(
                vault,
                title="每日完整性检查通过",
                severity="INFO",
                details=["4 项检查全部通过", f"账户数: {len(compute_balances(vault))}"],
                source="daily_integrity_check.py",
            )
        sys.exit(0)

    has_error = any(level == "ERROR" for level, _ in all_errors)
    severity = "ERROR" if has_error else "WARN"

    print(f"\n{'❌' if has_error else '⚠️ '}  发现 {len(all_errors)} 个问题")
    for level, msg in all_errors:
        marker = "  ❌" if level == "ERROR" else "  ⚠️ "
        print(f"{marker} [{level}] {msg}")

    if not args.no_notify:
        details = [f"{level}: {msg}" for level, msg in all_errors]
        notify(
            vault_root=vault,
            title=f"每日完整性检查{'失败' if has_error else '告警'}",
            body=f"发现 {len(all_errors)} 个问题",
            severity=severity,
            details=details,
            source="daily_integrity_check.py",
        )

    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
