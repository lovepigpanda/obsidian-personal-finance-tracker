"""
parsers.py - Frontmatter 解析、转账配对检测

零依赖（仅 Python 标准库），所有脚本通用。
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Frontmatter 分隔符
FRONTMATTER_DELIM = "---"


def parse_frontmatter(filepath: str) -> Tuple[Dict, str]:
    """
    解析 .md 文件的 YAML 风格 frontmatter。

    Returns:
        (frontmatter_dict, body_text)
        如果文件没有 frontmatter，返回 ({}, body_text)
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        return ({}, f"")

    lines = content.split("\n")
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return ({}, content)

    # 找第二个 ---
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            end_idx = i
            break

    if end_idx is None:
        return ({}, content)

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])

    fm = _parse_simple_yaml(fm_lines)
    return (fm, body)


def _parse_simple_yaml(lines: List[str]) -> Dict:
    """
    极简 YAML 解析器 — 只支持本项目用到的语法：
    - key: value
    - key: [a, b, c]   (inline list)
    - key: "quoted value"
    - key: number
    """
    result = {}
    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z_][\w-]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key = m.group(1).strip()
        value = m.group(2).strip()
        result[key] = _coerce_value(value)
    return result


def _coerce_value(raw: str):
    """把字符串值转成合适类型。"""
    if not raw:
        return ""

    # Inline list: [a, b, c]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_coerce_value(x.strip()) for x in inner.split(",")]

    # Quoted string
    if (raw.startswith('"') and raw.endswith('"')) or (
        raw.startswith("'") and raw.endswith("'")
    ):
        return raw[1:-1]

    # Boolean
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False

    # Number
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        pass

    # Plain string
    return raw


def find_accounts_file(vault_root: str) -> Optional[str]:
    """
    在 vault 根目录下找账户列表文件。
    优先 Accounts/account-list.md，回退到任意 account*.md
    """
    candidates = [
        os.path.join(vault_root, "Accounts", "account-list.md"),
        os.path.join(vault_root, "Accounts", "accounts.md"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c

    # 兜底
    acc_dir = os.path.join(vault_root, "Accounts")
    if os.path.isdir(acc_dir):
        for f in os.listdir(acc_dir):
            if f.lower().startswith("account") and f.endswith(".md"):
                return os.path.join(acc_dir, f)
    return None


def parse_accounts(vault_root: str) -> Dict[str, Dict]:
    """
    从 account-list.md 解析账户表，返回 {account_name: {currency, initial_balance, ...}}

    支持的列 (按列名匹配, 不依赖列顺序):
        - 账户 / Account / 账户名 / Account Name  -> name
        - 类型 / Type                              -> type
        - 币种 / Currency                          -> currency
        - 初始余额 / Initial Balance                -> initial_balance
        - 账单日 / Statement Day                    -> statement_day (int, 信用卡)
        - 还款日 / Due Day                          -> due_day (int, 信用卡)
        - 信用额度 / Credit Limit                  -> credit_limit
    """
    acc_file = find_accounts_file(vault_root)
    if not acc_file:
        return {}

    fm, body = parse_frontmatter(acc_file)

    # 列名别名 (zh + en)
    col_aliases = {
        "name": ["账户", "账户名", "Account", "Account Name", "Name"],
        "type": ["类型", "Type"],
        "currency": ["币种", "Currency"],
        "initial_balance": ["初始余额", "Initial Balance", "Initial"],
        "statement_day": ["账单日", "Statement Day", "Statement"],
        "due_day": ["还款日", "Due Day", "Due"],
        "credit_limit": ["信用额度", "Credit Limit", "Limit"],
    }

    header_cols = []  # 头部: [(role, idx), ...]
    accounts = {}

    for line in body.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        if re.match(r"^\|[\s\-:|]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]

        if not header_cols:
            # 第一行表头
            for idx, cell in enumerate(cells):
                cell_clean = cell.strip()
                for role, aliases in col_aliases.items():
                    if cell_clean in aliases:
                        header_cols.append((role, idx))
                        break
            continue

        if not header_cols:
            continue

        # 解析行
        row = {role: (cells[idx] if idx < len(cells) else "") for role, idx in header_cols}
        name = row.get("name", "")
        if not name:
            continue

        # 类型化
        currency = row.get("currency", "CNY") or "CNY"
        try:
            initial = float(row.get("initial_balance", "0") or "0")
        except ValueError:
            initial = 0.0

        def _int(s):
            try:
                return int(s) if s and s != "-" else None
            except ValueError:
                return None

        accounts[name] = {
            "currency": currency,
            "type": row.get("type", ""),
            "initial_balance": initial,
            "statement_day": _int(row.get("statement_day", "")),
            "due_day": _int(row.get("due_day", "")),
            "credit_limit": _int(row.get("credit_limit", "")),
            "row": cells,
        }
    return accounts


def find_transaction_files(vault_root: str) -> List[str]:
    """
    扫描所有交易 .md 文件（expenses/incomes/transfers/{out,in}）。
    """
    base = os.path.join(vault_root, "Transactions")
    if not os.path.isdir(base):
        return []

    results = []
    for sub in ("expenses", "incomes"):
        d = os.path.join(base, sub)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith(".md"):
                    results.append(os.path.join(d, f))

    transfers_dir = os.path.join(base, "transfers")
    for sub in ("out", "in"):
        d = os.path.join(transfers_dir, sub)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith(".md"):
                    results.append(os.path.join(d, f))

    return sorted(results)


def find_transfer_pair(
    vault_root: str, pair_id: str, direction: Optional[str] = None
) -> List[str]:
    """
    找同一 transfer_pair_id 的所有文件。
    direction: 'out' / 'in' / None (all)
    """
    if not pair_id:
        return []
    base = os.path.join(vault_root, "Transactions", "transfers")
    dirs = []
    if direction in (None, "out"):
        dirs.append(os.path.join(base, "out"))
    if direction in (None, "in"):
        dirs.append(os.path.join(base, "in"))

    matches = []
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if not f.endswith(".md"):
                continue
            fp = os.path.join(d, f)
            fm, _ = parse_frontmatter(fp)
            if fm.get("transfer_pair_id") == pair_id:
                matches.append(fp)
    return matches


def file_status(filepath: str) -> str:
    """读 status 字段，默认 ACTIVE。"""
    fm, _ = parse_frontmatter(filepath)
    return fm.get("status", "ACTIVE")
