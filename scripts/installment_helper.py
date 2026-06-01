#!/usr/bin/env python3
"""
installment_helper.py - 分期摊销模板生成器 (#24)

用法:
    python3 installment_helper.py create --first-file <path> --total N [--start-date YYYY-MM-DD]
    # 在用户写入"第一期" expense 文件后调用此脚本, 自动生成剩余 N-1 期的占位模板

逻辑:
    1. 读第一期 expense 的 frontmatter (amount, currency, account, category, note)
    2. 用 installment_group_id 关联所有期
    3. 生成剩余 N-1 个 expense 模板 (日期递增), 标记 status=PENDING
    4. 用户实际扣款时, 改 status=ACTIVE + 调 validate_transaction.py
"""

import argparse
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.parsers import parse_frontmatter


def generate_installments(first_file: str, total: int, start_date: str = None):
    """
    从第一期生成 N 个分期 expense 文件。
    第一个文件是 ACTIVE (已发生), 其余是 PENDING (待扣款)。
    """
    if not os.path.exists(first_file):
        print(f"❌ 文件不存在: {first_file}", file=sys.stderr)
        sys.exit(1)

    fm, body = parse_frontmatter(first_file)
    if not fm:
        print(f"❌ 无法解析 frontmatter: {first_file}", file=sys.stderr)
        sys.exit(1)

    if fm.get("type") != "expense":
        print(f"❌ 第一期必须是 expense 类型, 当前: {fm.get('type')}", file=sys.stderr)
        sys.exit(1)

    if total < 2:
        print(f"❌ 分期数必须 ≥ 2, 当前: {total}", file=sys.stderr)
        sys.exit(1)

    # 取第一期日期
    if start_date:
        first_date = date.fromisoformat(start_date)
    else:
        first_date = date.fromisoformat(str(fm.get("date", date.today().isoformat())))

    # group_id
    group_id = fm.get("installment_group_id")
    if not group_id:
        # 自动生成
        group_id = f"INS-{first_date.isoformat()}-{fm.get('account', 'acc')}-{int(fm.get('amount', 0))}"
        print(f"ℹ️  自动生成 installment_group_id: {group_id}")
        # 回写第一期 (把 group_id 加到 frontmatter)
        _update_frontmatter(first_file, {"installment_group_id": group_id})

    # 取文件名 (相对 vault 路径)
    rel_path = first_file
    if "/Transactions/expenses/" in first_file:
        fname = os.path.basename(first_file)
    else:
        print(f"❌ 第一期文件必须在 Transactions/expenses/ 下", file=sys.stderr)
        sys.exit(1)

    # 提取命名模式: {date}-{title}-{amount}-{currency}-{status}.md
    # 例: 2026-04-15-expense-iphone-500-CNY-ACTIVE.md
    # 提取 title 部分: 第一个 '-' 后, 倒数 3 段前
    fname_no_ext = fname.replace(".md", "")
    parts = fname_no_ext.rsplit("-", 3)  # ['2026-04-15-expense-iphone', '500', 'CNY', 'ACTIVE']
    base_with_date = parts[0]  # 2026-04-15-expense-iphone
    amount = int(parts[1]) if parts[1].isdigit() else int(float(fm.get("amount", 0)))
    currency = parts[2]
    # 从 base_with_date 去掉日期前缀
    title_part = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", base_with_date)  # expense-iphone

    out_dir = os.path.dirname(first_file)
    created = [first_file]  # 第一期已存在

    for i in range(2, total + 1):
        next_date = first_date + timedelta(days=30 * (i - 1))  # 简化: 每月 30 天后
        next_fname = f"{next_date.isoformat()}-{title_part}-{amount}-{currency}-PENDING.md"
        next_fpath = os.path.join(out_dir, next_fname)

        # 写 PENDING 文件
        new_fm = dict(fm)
        new_fm["date"] = next_date.isoformat()
        new_fm["status"] = "PENDING"
        new_fm["installment_index"] = i
        new_fm["installment_total"] = total
        new_fm["installment_group_id"] = group_id

        _write_md(next_fpath, new_fm, body)
        created.append(next_fpath)
        print(f"  ✅ 第 {i}/{total} 期: {next_fname}")

    # 给第一期补 installment_index/total
    _update_frontmatter(first_file, {
        "installment_index": 1,
        "installment_total": total,
    })
    print(f"\n✅ 共生成 {len(created)} 期 (第 1 期已 ACTIVE, {len(created) - 1} 期 PENDING)")


def _update_frontmatter(filepath: str, updates: dict):
    """原地更新 frontmatter 字段"""
    with open(filepath) as f:
        content = f.read()

    for key, value in updates.items():
        # 替换或添加
        pattern = rf"^{key}:.*$"
        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(pattern, f"{key}: {value}", content, count=1, flags=re.MULTILINE)
        else:
            # 在 frontmatter 末尾插入
            content = re.sub(
                r"^---\n",
                f"---\n{key}: {value}\n",
                content,
                count=1,
            )
    with open(filepath, "w") as f:
        f.write(content)


def _write_md(filepath: str, fm: dict, body: str):
    """写新的 md 文件, frontmatter 用 YAML 块"""
    lines = ["---"]
    for k, v in fm.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    # body 已经是去掉 frontmatter 的内容
    if body.strip():
        lines.append(body.strip())
    with open(filepath, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description="分期摊销模板生成器 (#24)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="从第一期生成 N 期")
    c.add_argument("--first-file", required=True, help="第一期文件绝对路径")
    c.add_argument("--total", type=int, required=True, help="总期数 (≥ 2)")
    c.add_argument("--start-date", default=None, help="第一期日期 (YYYY-MM-DD), 默认读第一期文件")

    args = ap.parse_args()
    if args.cmd == "create":
        generate_installments(args.first_file, args.total, args.start_date)


if __name__ == "__main__":
    main()
