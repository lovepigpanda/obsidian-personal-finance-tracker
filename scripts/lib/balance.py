"""
balance.py - 余额计算核心

路径 A（DataviewJS 仪表盘）和路径 B（Python 校验脚本）共用同一份算法。
这是保证两个独立计算路径结果一致的根本。

公式（每个账户、每种币种独立算）：
    balance(account, currency) = initial_balance
                              + sum(income where account=this and currency=this)
                              - sum(expense where account=this and currency=this)
                              - sum(transfer-out where from_account=this and currency=this)
                              + sum(transfer-in where to_account=this and currency=this)
"""

import os
from collections import defaultdict
from typing import Dict, List, Tuple

from .parsers import (
    find_transaction_files,
    parse_accounts,
    parse_frontmatter,
    file_status,
)


def compute_balances(vault_root: str) -> Dict[Tuple[str, str], float]:
    """
    计算每个 (账户, 币种) 的当前余额。

    Returns:
        {(account_name, currency): balance}
    """
    accounts = parse_accounts(vault_root)
    # 先用初始余额填 0
    balances = defaultdict(float)
    for name, info in accounts.items():
        balances[(name, info["currency"])] = info["initial_balance"]

    # 遍历所有交易
    for filepath in find_transaction_files(vault_root):
        if file_status(filepath) != "ACTIVE":
            continue
        fm, _ = parse_frontmatter(filepath)
        if not fm:
            continue

        tx_type = fm.get("type")
        amount = _safe_float(fm.get("amount"))
        currency = fm.get("currency", "CNY")
        if amount <= 0:
            continue

        if tx_type == "expense":
            account = fm.get("account")
            if account:
                balances[(account, currency)] -= amount

        elif tx_type == "income":
            account = fm.get("account")
            if account:
                balances[(account, currency)] += amount

        elif tx_type == "transfer":
            from_acc = fm.get("from_account")
            to_acc = fm.get("to_account")
            if not from_acc or not to_acc:
                continue
            # 区分方向：看目录
            if filepath.endswith("/out/" + os.path.basename(filepath)) or "/transfers/out/" in filepath:
                balances[(from_acc, currency)] -= amount
            elif "/transfers/in/" in filepath:
                balances[(to_acc, currency)] += amount
            else:
                # 兜底：根据字段判断
                # 如果文件在 transfers 根目录，看 from/to 哪个出现
                # (本项目约定文件一定在 out/ 或 in/，这里只是安全网)
                pass

    return dict(balances)


def compute_currency_totals(
    vault_root: str,
) -> Dict[str, Dict[str, float]]:
    """
    按币种汇总总流入、总流出（用于守恒检查）。

    Returns:
        {
            'CNY': {
                'income': 12345.0,
                'expense': 6789.0,
                'transfer_in': 5000.0,
                'transfer_out': 5000.0,
                'net_change': 1556.0,
            },
            ...
        }
    """
    totals = defaultdict(
        lambda: {"income": 0.0, "expense": 0.0, "transfer_in": 0.0, "transfer_out": 0.0}
    )

    for filepath in find_transaction_files(vault_root):
        if file_status(filepath) != "ACTIVE":
            continue
        fm, _ = parse_frontmatter(filepath)
        if not fm:
            continue

        tx_type = fm.get("type")
        amount = _safe_float(fm.get("amount"))
        currency = fm.get("currency", "CNY")
        if amount <= 0:
            continue

        if tx_type == "expense":
            totals[currency]["expense"] += amount
        elif tx_type == "income":
            totals[currency]["income"] += amount
        elif tx_type == "transfer":
            if "/transfers/out/" in filepath:
                totals[currency]["transfer_out"] += amount
            elif "/transfers/in/" in filepath:
                totals[currency]["transfer_in"] += amount

    # 加 net_change
    for ccy, data in totals.items():
        data["net_change"] = (
            data["income"] - data["expense"] - data["transfer_out"] + data["transfer_in"]
        )

    return dict(totals)


def _safe_float(v) -> float:
    """转 float，失败返 0。"""
    if v is None or v == "":
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0
