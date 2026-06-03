"""
learning_tracker.py — 用户习惯学习机制

行为:
1. 第一次用默认账户记账 → 静默记录到 ~/.obsidian-finance/learning.json
2. 第二次同 keyword 但选了不同账户 → 询问用户
3. 用户确认后:
   - 如果选新账户 → 更新 learning (新账户, count+1)
   - 如果保持原默认 → 不动
4. learning key = note 里提取的 2 字关键词 (中文)

数据结构:
{
  "version": "V1.0",
  "patterns": {
    "地铁": {"account": "交通卡", "count": 3, "last_used": "2026-06-03", "category": "Transport"},
    "沙县": {"account": "Alipay", "count": 1, "last_used": "2026-06-02", "category": "Food"}
  }
}
"""

import json
import os
import re
from datetime import date
from typing import Any, Dict, List, Optional, Tuple


def get_learning_path(store_path: str) -> str:
    """
    store_path 可能是:
    - 完整文件路径: ~/.obsidian-finance/learning.json
    - 目录: ~/.obsidian-finance/
    默认文件名: learning.json
    """
    if store_path.endswith(".json"):
        return store_path
    return os.path.join(store_path, "learning.json")


def load_learning(store_path: str) -> Dict[str, Any]:
    """加载 learning.json, 不存在返空 dict。"""
    path = get_learning_path(store_path)
    if not os.path.isfile(path):
        return {"version": "V1.0", "patterns": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"version": "V1.0", "patterns": {}}


def save_learning(store_path: str, data: Dict[str, Any]) -> None:
    """写 learning.json。"""
    path = get_learning_path(store_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def extract_keywords(note: str, max_keywords: int = 2) -> List[str]:
    """
    从 note 提取关键词 (用于 learning key)。
    简单实现: 2-4 字中文片段 (避开 "今天/昨天/中午" 等时间词)。
    """
    if not note:
        return []

    # 时间/虚词停用
    stopwords = {
        "今天", "昨天", "前天", "明天", "中午", "下午", "晚上", "上午", "早上",
        "我", "你", "他", "她", "它", "了", "的", "在", "是", "有", "和", "也",
        "都", "才", "就", "要", "去", "来", "吧", "吗", "呢", "啊", "嗯", "哦",
    }

    # 提取 2-4 字片段 (中文)
    # 1. 标点切分
    tokens = re.split(r"[，。！？、,.\!?\s]+", note)
    keywords = []
    for tok in tokens:
        # 提取 2-4 字连续中文
        for m in re.finditer(r"[\u4e00-\u9fff]{2,4}", tok):
            word = m.group(0)
            if word in stopwords:
                continue
            if word not in keywords:
                keywords.append(word)
                if len(keywords) >= max_keywords:
                    return keywords

    return keywords


def record_usage(
    store_path: str,
    category: str,
    note: str,
    account: str,
) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    记录一次默认账户使用, 返回 (conflict_message, updated_learning)。

    conflict_message:
      - None: 无冲突, 已记录
      - str: 第二次用了不同账户, 询问用户

    updated_learning: 当前完整 learning 数据
    """
    learning = load_learning(store_path)
    patterns = learning.get("patterns", {})
    keywords = extract_keywords(note)

    if not keywords:
        return None, learning

    # 检查每个 keyword 是否有冲突
    for kw in keywords:
        if kw not in patterns:
            continue
        existing = patterns[kw]
        if existing.get("account") != account:
            # 冲突 — 第二次用不同账户
            return (
                f"你这次 {note} 用 {account}, 但之前 {kw} 类都是用 {existing.get('account')} ({existing.get('count', 1)} 次), 改默认吗?",
                learning,
            )

    # 无冲突, 静默记录
    today = date.today().isoformat()
    for kw in keywords:
        if kw in patterns and patterns[kw].get("account") == account:
            # 同一账户, count+1
            patterns[kw]["count"] = patterns[kw].get("count", 1) + 1
            patterns[kw]["last_used"] = today
        else:
            # 新 keyword
            patterns[kw] = {
                "account": account,
                "count": 1,
                "last_used": today,
                "category": category,
            }

    learning["patterns"] = patterns
    save_learning(store_path, learning)
    return None, learning


def confirm_update(
    store_path: str,
    category: str,
    note: str,
    new_account: str,
    user_confirmed: bool,
) -> Dict[str, Any]:
    """
    用户回应冲突询问 (yes/no)。
    user_confirmed=True: 更新默认到新账户。
    user_confirmed=False: 保持原默认, 不动。
    """
    learning = load_learning(store_path)
    patterns = learning.get("patterns", {})
    keywords = extract_keywords(note)

    if not user_confirmed:
        # 保持原默认, 只更新 last_used / count (表示"用户坚持用原默认")
        for kw in keywords:
            if kw in patterns:
                patterns[kw]["last_used"] = date.today().isoformat()
        learning["patterns"] = patterns
        save_learning(store_path, learning)
        return learning

    # 确认 → 更新默认到 new_account
    today = date.today().isoformat()
    for kw in keywords:
        if kw in patterns:
            old_count = patterns[kw].get("count", 1)
            patterns[kw] = {
                "account": new_account,
                "count": old_count + 1,
                "last_used": today,
                "category": category,
            }
        else:
            patterns[kw] = {
                "account": new_account,
                "count": 1,
                "last_used": today,
                "category": category,
            }

    learning["patterns"] = patterns
    save_learning(store_path, learning)
    return learning
