#!/usr/bin/env python3
"""
test_incremental_balance.py - V1.4 增量余额快照 e2e 测试

项目无 pytest, 无 tests/ 目录 (SKILL.md 文档误述, 真实状态是只有 10 个脚本)。
本测试用 stdlib unittest, 跟项目"stdlib 零依赖"原则一致。

测试隔离: 每个 case 用 tempfile.mkdtemp 建独立 vault, 测试结束清理,
不污染 ~/Obsidian/finance/ 真实数据。

测试覆盖 (4 个核心 case, 跟方案 B 设计对齐):
  1. test_incremental_expense: 写 1 笔 expense → balances.md mtime 变 + 受影响账户值对 + 其他账户不变
  2. test_incremental_transfer: 写 1 笔 transfer → 2 个账户都更新, 其他账户不变
  3. test_fallback_when_no_existing: 删 balances.md 后写笔 → 自动 fallback 全量重算 (不崩)
  4. test_daily_full_refresh: daily 跑后 source 字段 = "daily_integrity_check.py" (不污染)

设计原则:
  - 不依赖任何外部 fixture, 每个 case 自建 vault
  - 不需要 agent-config.md (gate 跳过, V1.3.4 + _onboarding_gate.py 软跳过)
  - 真实跑 create_transaction() 走完整 IO, 不 mock
"""
import os
import sys
import shutil
import tempfile
import time
import unittest
from datetime import datetime

# 让 transaction_create.py 和 lib/ 可 import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_SCRIPTS = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SKILL_SCRIPTS)

from transaction_create import create_transaction
from lib.balance import (
    compute_balances,
    read_existing_balances,
    refresh_balance_snapshot_incremental,
    write_balance_snapshot,
)


def _make_minimal_vault(tmpdir: str) -> str:
    """
    建一个最小可跑 vault:
      - Accounts/account-list.md (markdown 表格格式, 跟 parse_accounts 真实数据一致)
      - Transactions/{expenses,incomes,transfers/{out,in}}/
    不建 agent-config.md (V1.3.4 gate 软跳过, 不阻塞核心 IO)
    """
    vault = tmpdir
    os.makedirs(os.path.join(vault, "Accounts"), exist_ok=True)
    for sub in [
        "Transactions/expenses",
        "Transactions/incomes",
        "Transactions/transfers/out",
        "Transactions/transfers/in",
    ]:
        os.makedirs(os.path.join(vault, sub), exist_ok=True)

    # account-list.md (markdown 表格, parse_accounts 真认这格式, 不用 frontmatter)
    account_list = """# 账户列表

| 账户 | 类型 | 币种 | 初始余额 |
|------|------|------|----------|
| Alipay | e-wallet | CNY | 1000.00 |
| CMB | bank | CNY | 5000.00 |
| Cash | cash | CNY | 200.00 |
| 交通卡 | e-wallet | CNY | 50.00 |
"""
    with open(os.path.join(vault, "Accounts", "account-list.md"), "w", encoding="utf-8") as f:
        f.write(account_list)
    return vault


class TestIncrementalBalance(unittest.TestCase):
    """V1.4 增量余额快照 4 个核心 case"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="finance-test-")
        self.vault = _make_minimal_vault(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --------------------------------------------------------------
    # Case 1: 写 1 笔 expense → 1 个账户刷新, 其他 3 个账户不变
    # --------------------------------------------------------------
    def test_incremental_expense(self):
        """写 1 笔 Alipay -100 expense → Alipay 余额立刻变, 其他账户保留旧值"""
        # 1. 先做一次 daily 全量刷新建立 baseline
        snapshot_path = write_balance_snapshot(self.vault, source="daily_integrity_check.py")
        self.assertTrue(snapshot_path, "baseline 快照应写入成功")
        baseline = read_existing_balances(self.vault)
        self.assertIsNotNone(baseline, "baseline 应可读出")
        self.assertEqual(baseline[("Alipay", "CNY")], 1000.00)
        self.assertEqual(baseline[("CMB", "CNY")], 5000.00)

        # 2. 写 1 笔 expense: Alipay -100
        result = create_transaction(
            vault_root=self.vault,
            type_="expense",
            date_=datetime.now().strftime("%Y-%m-%d"),
            amount=100.0,
            currency="CNY",
            category="Food",
            note="午餐测试",
            account="Alipay",
        )
        self.assertTrue(result["ok"], f"create_transaction 应成功: {result}")
        self.assertIn("balance_snapshot", result, "V1.4 应返回 balance_snapshot 字段")
        self.assertEqual(
            result["balance_snapshot"]["trigger"], "incremental",
            "增量刷新应标 trigger=incremental"
        )
        self.assertEqual(
            result["balance_snapshot"]["affected_accounts"], ["Alipay"],
            "expense 写笔应只影响 1 个账户"
        )

        # 3. 验证 balances.md: Alipay 变成 900, 其他 3 个账户仍是 baseline 值
        after = read_existing_balances(self.vault)
        self.assertIsNotNone(after)
        self.assertAlmostEqual(after[("Alipay", "CNY")], 900.00, places=2,
                               msg="Alipay 应减 100 → 900")
        self.assertAlmostEqual(after[("CMB", "CNY")], 5000.00, places=2,
                               msg="CMB 未受影响, 应保持 5000")
        self.assertAlmostEqual(after[("Cash", "CNY")], 200.00, places=2,
                               msg="Cash 未受影响, 应保持 200")
        self.assertAlmostEqual(after[("交通卡", "CNY")], 50.00, places=2,
                               msg="交通卡 未受影响, 应保持 50")

        # 4. 验证 source 字段是 transaction_create.py (不是 daily)
        with open(snapshot_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("source: transaction_create.py", content,
                      "source 字段应反映写笔触发的来源")
        # baseline 是 daily, 增量后是 transaction_create.py
        self.assertNotIn("source: daily_integrity_check.py", content,
                         "增量刷新后不应再有 daily source")

    # --------------------------------------------------------------
    # Case 2: 写 1 笔 transfer → 2 个账户都刷新, 其他不变
    # --------------------------------------------------------------
    def test_incremental_transfer(self):
        """写 1 笔 Alipay → CMB 转 300 → 两个账户都更新, Cash / 交通卡 不动"""
        # 1. baseline
        write_balance_snapshot(self.vault, source="daily_integrity_check.py")
        baseline_cash = read_existing_balances(self.vault)[("Cash", "CNY")]

        # 2. transfer
        result = create_transaction(
            vault_root=self.vault,
            type_="transfer",
            date_=datetime.now().strftime("%Y-%m-%d"),
            amount=300.0,
            currency="CNY",
            category="Transfer",
            note="调拨测试",
            account="Alipay",
            to_account="CMB",
        )
        self.assertTrue(result["ok"], f"transfer 应成功: {result}")
        self.assertEqual(result["balance_snapshot"]["affected_accounts"],
                         ["Alipay", "CMB"],
                         "transfer 应影响 2 个账户")
        self.assertIn("transfer_pair_id", result)

        # 3. 验证
        after = read_existing_balances(self.vault)
        self.assertAlmostEqual(after[("Alipay", "CNY")], 700.00, places=2,
                               msg="Alipay 减 300")
        self.assertAlmostEqual(after[("CMB", "CNY")], 5300.00, places=2,
                               msg="CMB 加 300")
        self.assertEqual(after[("Cash", "CNY")], baseline_cash,
                         msg="Cash 未受影响, 应保持")

    # --------------------------------------------------------------
    # Case 3: 旧 balances.md 不存在 → 增量自动 fallback 全量
    # --------------------------------------------------------------
    def test_fallback_when_no_existing_snapshot(self):
        """没有旧 balances.md → 第一次写笔也能正常工作 (fallback 全量)"""
        # 不调 write_balance_snapshot, 没有 balances.md
        balances_path = os.path.join(self.vault, "Accounts", "balances.md")
        self.assertFalse(os.path.exists(balances_path), "应确认 baseline 不存在")

        # 写 1 笔
        result = create_transaction(
            vault_root=self.vault,
            type_="expense",
            date_=datetime.now().strftime("%Y-%m-%d"),
            amount=50.0,
            currency="CNY",
            category="Transport",
            note="地铁测试",
            account="交通卡",
        )
        self.assertTrue(result["ok"], f"应成功: {result}")
        # fallback 时仍走增量入口, 但 merged = new_full (因为 existing 是 None)
        self.assertEqual(result["balance_snapshot"]["trigger"], "incremental")

        # 验证 balances.md 被创建 + 余额正确
        self.assertTrue(os.path.exists(balances_path), "fallback 后 balances.md 应被创建")
        after = read_existing_balances(self.vault)
        self.assertIsNotNone(after)
        self.assertAlmostEqual(after[("交通卡", "CNY")], 0.00, places=2,
                               msg="交通卡 50-50=0")

    # --------------------------------------------------------------
    # Case 4: daily 跑后 source 字段 = "daily_integrity_check.py"
    #         (确认我没把 daily 的 source 字段改坏)
    # --------------------------------------------------------------
    def test_daily_full_refresh_source_field(self):
        """daily write_balance_snapshot 应正确写 source=daily_integrity_check.py"""
        path = write_balance_snapshot(self.vault, source="daily_integrity_check.py")
        self.assertTrue(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("source: daily_integrity_check.py", content,
                      "daily 刷新应保留 source 字段")


class TestIncrementalVsFullConsistency(unittest.TestCase):
    """
    Case 5 (关键正确性): 增量刷新 vs 全量刷新结果应该**完全一致**
    这是 V1.4 的核心保证 — 不能因为"优化"导致数据不一致
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="finance-test-consistency-")
        self.vault = _make_minimal_vault(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_incremental_equals_full_after_write(self):
        """写 3 笔后, 增量刷新结果 == 全量 compute_balances 结果"""
        # 写 3 笔: 1 expense, 1 income, 1 transfer
        today = datetime.now().strftime("%Y-%m-%d")
        r1 = create_transaction(
            vault_root=self.vault, type_="expense", date_=today,
            amount=120.0, currency="CNY", category="Food", note="t1", account="Alipay",
        )
        r2 = create_transaction(
            vault_root=self.vault, type_="income", date_=today,
            amount=3000.0, currency="CNY", category="Salary", note="t2", account="CMB",
        )
        r3 = create_transaction(
            vault_root=self.vault, type_="transfer", date_=today,
            amount=500.0, currency="CNY", category="Transfer", note="t3",
            account="Alipay", to_account="CMB",
        )
        for r in (r1, r2, r3):
            self.assertTrue(r["ok"], f"每笔都应成功: {r}")

        # 1. 增量刷新结果 (已经是上面 3 笔写完后最近一次)
        incremental = read_existing_balances(self.vault)

        # 2. 全量重算 (真相源)
        full = compute_balances(self.vault)

        # 3. 断言: 增量 == 全量
        self.assertEqual(
            set(incremental.keys()), set(full.keys()),
            "增量刷新和全量重算应覆盖完全相同的账户集合"
        )
        for key in full:
            self.assertAlmostEqual(
                incremental[key], full[key], places=2,
                msg=f"{key}: 增量 {incremental[key]} != 全量 {full[key]}"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
