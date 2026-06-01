#!/usr/bin/env python3
"""
installment_check.py - 分期完整性检查 (#24)

用法:
    python3 installment_check.py [--vault <vault_root>]

逻辑:
    1. 扫所有 expense 文件, 按 installment_group_id 分组
    2. 检查每组: 总期数与实际文件数是否一致
    3. 检查每期: 金额一致, 账户一致, 分类一致, 货币一致
    4. 检查 PENDING → ACTIVE 状态: 当前日期 ≥ 文件日期 且 status=PENDING → 提醒"该扣款了"
    5. 检查孤立分期: 只有 1 期但 is_installment=true (用户改了主意)
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import find_transaction_files, parse_frontmatter, file_status
from lib.notifier import notify


def check_installments(vault_root: str) -> list:
    """检查所有分期组, 返回 (level, message) 列表。"""
    errors = []
    today = date.today()

    # 按 group_id 聚合
    groups = defaultdict(list)  # group_id -> [(filepath, fm), ...]
    for filepath in find_transaction_files(vault_root):
        if file_status(filepath) != "ACTIVE" and file_status(filepath) != "PENDING":
            continue
        fm, _ = parse_frontmatter(filepath)
        if not fm:
            continue
        if fm.get("type") != "expense":
            continue
        gid = fm.get("installment_group_id")
        if gid:
            groups[gid].append((filepath, fm))

    if not groups:
        return errors

    for gid, items in groups.items():
        if len(items) == 1:
            fm = items[0][1]
            if fm.get("is_installment") or fm.get("installment_total"):
                errors.append((
                    "WARN",
                    f"分期组 {gid} 只有 1 期, 但标记为分期, 确认是分 1 期还是漏生成?"
                ))
            continue

        # 校验期数
        total_expected = items[0][1].get("installment_total")
        if total_expected and len(items) != total_expected:
            errors.append((
                "ERROR",
                f"分期组 {gid}: 期望 {total_expected} 期, 实际 {len(items)} 期, 缺 {total_expected - len(items)} 期"
            ))

        # 校验一致性: amount, account, category, currency
        first_fm = items[0][1]
        for filepath, fm in items[1:]:
            for field in ("amount", "currency", "account", "category"):
                if fm.get(field) != first_fm.get(field):
                    fname = os.path.basename(filepath)
                    errors.append((
                        "ERROR",
                        f"分期 {fname} ({gid}) 的 {field}={fm.get(field)} 与第一期 {first_fm.get(field)} 不一致"
                    ))

        # 检查 PENDING 是否该扣款
        for filepath, fm in items:
            status = file_status(filepath)
            if status != "PENDING":
                continue
            d_str = str(fm.get("date", ""))
            try:
                d = date.fromisoformat(d_str)
            except (ValueError, TypeError):
                continue
            if d <= today:
                idx = fm.get("installment_index", "?")
                total = fm.get("installment_total", "?")
                fname = os.path.basename(filepath)
                errors.append((
                    "WARN",
                    f"💳 分期 {fname} (第 {idx}/{total} 期) 已到扣款日 ({d}), 但仍为 PENDING 状态, 确认扣款后改 status=ACTIVE"
                ))

    return errors


def main():
    ap = argparse.ArgumentParser(description="分期完整性检查 (#24)")
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
    errors = check_installments(vault)

    if not errors:
        print("✅ 无分期异常")
        sys.exit(0)

    has_error = any(l == "ERROR" for l, _ in errors)
    severity = "ERROR" if has_error else "WARN"

    for level, msg in errors:
        marker = "  ❌" if level == "ERROR" else "  ⚠️ "
        print(f"{marker} [{level}] {msg}")

    if not args.no_notify:
        details = [f"[{l}] {m}" for l, m in errors]
        notify(
            vault_root=vault,
            title="💳 分期检查",
            body=f"发现 {len(errors)} 个分期问题",
            severity=severity,
            details=details,
            source="installment_check.py",
        )
    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
