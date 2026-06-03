"""
parsers.py - Frontmatter 解析、转账配对检测

零依赖（仅 Python 标准库），所有脚本通用。
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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
        - 贷款总额 / Principal                      -> principal (float, 贷款)
        - 月供 / Monthly Payment                    -> monthly_payment (float, 贷款)
        - 月供日 / Payment Day                      -> payment_day (int 1-31, 贷款)
        - 合同总期数 / Total Months                 -> total_months (int, 贷款)
        - 剩余期数 / Remaining Months               -> remaining_months (int, 贷款, 可选)
        - 起始月 / Start Month                      -> start_month (str YYYY-MM, 贷款)

    贷款字段说明:
    - principal + monthly_payment + start_month + payment_day + total_months 是必填
    - remaining_months 可选, 如果提供则用于"已还+剩余=合同"一致性校验
    - payment_day 必须是 1-31 的真实扣款日, 脚本会按当月实际天数自动处理 (2 月 28/29, 30 天月等)

    兜底: 如果贷款 5 个必填列都为空, 尝试从"说明"列自然语言提取 (如
    "贷款总额 1500000 / 月供 9195.37 / 剩余 91 期 / 起始 2024-01")。
    这是给老用户向后兼容 — 新用户请用结构化列。
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
        "principal": ["贷款总额", "Principal", "Total"],
        "monthly_payment": ["月供", "Monthly Payment", "Monthly"],
        "payment_day": ["月供日", "Payment Day", "Payment Date"],
        "total_months": ["合同总期数", "贷款期数", "Total Months", "Term Months", "Total"],
        "remaining_months": ["剩余期数", "Remaining Months", "Remaining"],
        "start_month": ["起始月", "Start Month", "Start"],
        "note": ["说明", "Note", "Description"],
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

        def _float(s):
            try:
                return float(s) if s and s != "-" else None
            except ValueError:
                return None

        # 贷款字段: 优先结构化列, 全空时从"说明"列 regex 兜底
        principal = _float(row.get("principal", ""))
        monthly = _float(row.get("monthly_payment", ""))
        payment_day = _int(row.get("payment_day", ""))
        total = _int(row.get("total_months", ""))
        remaining = _int(row.get("remaining_months", ""))
        start = (row.get("start_month", "") or "").strip() or None

        if all(v is None or v == "" for v in (principal, monthly, payment_day, total, remaining, start)):
            note_text = row.get("note", "") or ""
            fallback = _parse_loan_note(note_text)
            principal = principal or fallback.get("principal")
            monthly = monthly or fallback.get("monthly_payment")
            payment_day = payment_day if payment_day is not None else fallback.get("payment_day")
            total = total if total is not None else fallback.get("total_months")
            remaining = remaining if remaining is not None else fallback.get("remaining_months")
            start = start or fallback.get("start_month")

        accounts[name] = {
            "currency": currency,
            "type": row.get("type", ""),
            "initial_balance": initial,
            "statement_day": _int(row.get("statement_day", "")),
            "due_day": _int(row.get("due_day", "")),
            "credit_limit": _int(row.get("credit_limit", "")),
            "principal": principal,
            "monthly_payment": monthly,
            "payment_day": payment_day,
            "total_months": total,
            "remaining_months": remaining,
            "start_month": start,
            "row": cells,
        }
    return accounts


def _parse_loan_note(note_text: str) -> Dict[str, Any]:
    """
    兜底: 从'说明'列自然语言提取贷款字段。

    格式: "贷款总额 1500000 / 月供 9195.37 / 月供日 25 / 240 期 / 起始 2024-01 / 平安银行"
    支持 zh (贷款总额/月供/月供日/期数/起始) 和 en (Principal/Monthly/Payment Day/Term/Start)。

    只在 5 个必填结构化列全空时调用。
    """
    result: Dict[str, Any] = {
        "principal": None,
        "monthly_payment": None,
        "payment_day": None,
        "total_months": None,
        "remaining_months": None,
        "start_month": None,
    }
    if not note_text:
        return result

    # 中文 key → 内部字段
    patterns_zh = [
        (r"贷款总额\s*[:：]?\s*([\d,]+\.?\d*)", "principal"),
        (r"月供\s*[:：]?\s*([\d,]+\.?\d*)", "monthly_payment"),
        (r"月供日\s*[:：]?\s*(\d{1,2})\s*[日号]?", "payment_day"),
        (r"剩余\s*(\d+)\s*期", "remaining_months"),
        (r"(?<!剩)总\s*(\d+)\s*期|(?<!剩)(\d+)\s*期总", "total_months"),  # "240 期总" / "总 240 期" / "240 期"
        (r"起始\s*[:：]?\s*(\d{4}-\d{2})", "start_month"),
    ]
    # 英文 key (兼容)
    patterns_en = [
        (r"[Pp]rincipal\s*[:：]?\s*([\d,]+\.?\d*)", "principal"),
        (r"[Mm]onthly(?:\s+[Pp]ayment)?\s*[:：]?\s*([\d,]+\.?\d*)", "monthly_payment"),
        (r"[Pp]ayment\s+[Dd]ay\s*[:：]?\s*(\d{1,2})", "payment_day"),
        (r"[Rr]emaining\s*[:：]?\s*(\d+)", "remaining_months"),
        (r"[Tt]erm(?:\s+[Mm]onths)?\s*[:：]?\s*(\d+)", "total_months"),
        (r"[Ss]tart(?:\s+[Mm]onth)?\s*[:：]?\s*(\d{4}-\d{2})", "start_month"),
    ]

    for pat, field in patterns_zh + patterns_en:
        m = re.search(pat, note_text)
        if not m:
            continue
        raw = m.group(1).replace(",", "")
        if field in ("principal", "monthly_payment"):
            try:
                result[field] = float(raw)
            except ValueError:
                pass
        elif field in ("payment_day", "remaining_months", "total_months"):
            try:
                result[field] = int(raw)
            except ValueError:
                pass
        else:  # start_month 字符串
            result[field] = raw

    return result


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
