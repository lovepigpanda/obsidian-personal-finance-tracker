"""
default_account_resolver.py — 默认账户解析器

工作流:
1. 用户输入 → 解析 (type, date, amount, category, note, account)
2. 若 user 已指定 account → 跳过, 直接用
3. 若 user 未指定 → 走 resolver:
   a. config/default_accounts.yaml 优先 (defaults 按顺序匹配)
   b. learning.json 兜底 (历史同 keyword)
   c. fallback (expense/income/transfer 默认)
4. 匹配时如发现 learning 有"用户曾用过 X 但本次用了 Y"且 X != Y 第一次 → 询问

API:
    resolve_default_account(category, note, account_list, config_path, learning, user_provided_account=None)
    -> {account, source, ask_message} | {account: None, ask_message: "..."}
"""

import os
import re
from typing import Any, Dict, List, Optional

from lib.parsers import parse_config_yaml


def load_config(config_path: str) -> Dict[str, Any]:
    """加载 config/default_accounts.yaml"""
    if not os.path.isfile(config_path):
        return {}
    return parse_config_yaml(config_path)


def match_rule(rule: Dict[str, Any], category: str, note: str) -> bool:
    """
    检查单条 rule 是否匹配 transaction。
    rule: {match: {category: <regex>, keyword: <regex>}, account, type, note}
    """
    if "match" not in rule:
        return False
    match = rule["match"]
    cat_pattern = match.get("category", ".*")
    kw_pattern = match.get("keyword", ".*")
    if not re.search(cat_pattern, category or ""):
        return False
    if not re.search(kw_pattern, note or ""):
        return False
    return True


def resolve_from_config(
    config: Dict[str, Any], category: str, note: str, account_names: List[str]
) -> Optional[Dict[str, Any]]:
    """
    从 config defaults 按顺序匹配, 返回第一个匹配的 rule (含 account + type 校验)。
    若匹配账户不在 account-list.md 里, 跳过 (WARN) 找下一个。
    """
    defaults = config.get("defaults", [])
    for rule in defaults:
        if match_rule(rule, category, note):
            account = rule.get("account")
            if not account:
                continue
            if account not in account_names:
                # 账户不存在, 跳过
                continue
            return rule
    return None


def resolve_from_learning(
    learning: Dict[str, Any], category: str, note: str, account_names: List[str]
) -> Optional[Dict[str, Any]]:
    """
    从 learning.json 找历史同 note 关键词的记录。
    关键词匹配: note 里的 2-4 字片段 (中文) 跟 learning key 前缀匹配。
    """
    patterns = learning.get("patterns", {})
    # patterns: {"keyword_prefix": {account, count, last_used, ...}}
    for keyword, entry in patterns.items():
        if re.search(re.escape(keyword), note or ""):
            account = entry.get("account")
            if account in account_names:
                return {
                    "account": account,
                    "source": "learning",
                    "keyword": keyword,
                    "count": entry.get("count", 1),
                }
    return None


def get_fallback(
    config: Dict[str, Any], transaction_type: str
) -> Optional[str]:
    """从 config.fallback 拿 type 对应的默认账户。transfer=ask 走单独路径。"""
    fallback = config.get("fallback", {})
    val = fallback.get(transaction_type, fallback.get("expense"))
    if val == "ask" or val is None:
        return None
    return val


def detect_account_from_note(
    note: str, account_names: List[str]
) -> Optional[str]:
    """
    从 note 里检测用户是否隐式提了账户 (e.g. "用招行买了" → CMB)。
    简单实现: note 里包含任一 account_name (中文 2 字以上)。
    """
    if not note:
        return None
    # 按名字长度倒序匹配 (避免 "CMB" 匹配了 "CMB Credit" 之前)
    for name in sorted(account_names, key=len, reverse=True):
        if len(name) >= 2 and name in note:
            return name
    return None


def resolve_default_account(
    category: str,
    note: str,
    account_names: List[str],
    config: Dict[str, Any],
    learning: Dict[str, Any],
    user_provided_account: Optional[str] = None,
) -> Dict[str, Any]:
    """
    主入口: 解析默认账户。

    Args:
        category: 交易类别 (e.g. "Food", "Transport")
        note: 交易备注 (e.g. "午餐沙县")
        account_names: 账户列表 (从 account-list.md 解析)
        config: load_config() 结果
        learning: load_learning() 结果
        user_provided_account: 用户显式指定的账户 (如果有, 直接用)

    Returns:
        {
            "account": <账户名> 或 None,
            "source": "user" | "config" | "learning" | "fallback" | "note" | None,
            "ask_message": str 或 None (Agent 收到 ask_message 应该 clarify)
        }
    """
    # 1. 用户显式指定 → 直接用
    if user_provided_account and user_provided_account in account_names:
        return {
            "account": user_provided_account,
            "source": "user",
            "ask_message": None,
        }

    # 2. note 里隐式提了账户
    note_account = detect_account_from_note(note, account_names)
    if note_account:
        return {
            "account": note_account,
            "source": "note",
            "ask_message": None,
        }

    # 3. config 优先匹配
    config_match = resolve_from_config(config, category, note, account_names)
    if config_match:
        return {
            "account": config_match.get("account"),
            "source": "config",
            "ask_message": None,
        }

    # 4. learning 兜底
    learning_match = resolve_from_learning(learning, category, note, account_names)
    if learning_match:
        return {
            "account": learning_match.get("account"),
            "source": "learning",
            "ask_message": None,
        }

    # 5. fallback
    # transaction_type 从调用方传入 (这里简化, 通过 note 推断)
    # 实际 transaction_create 会传 type
    fallback_account = get_fallback(config, "expense")  # 默认 expense
    if fallback_account and fallback_account in account_names:
        return {
            "account": fallback_account,
            "source": "fallback",
            "ask_message": None,
        }

    return {
        "account": None,
        "source": None,
        "ask_message": f"无法自动判断账户 (category={category}, note={note}), 请用户指定",
    }
