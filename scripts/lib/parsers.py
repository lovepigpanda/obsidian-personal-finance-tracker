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


def parse_config_yaml(filepath: str) -> Dict[str, Any]:
    """
    解析 config YAML 文件 (default_accounts.yaml 等)。

    支持:
    - 纯 YAML (无 frontmatter)
    - frontmatter `--- ... ---` 包裹的 YAML (跟 .md 一致)

    Returns:
        dict 解析结果
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return {}

    lines = content.split("\n")
    if not lines:
        return {}

    # 检测 frontmatter
    start = 0
    if lines[0].strip() == FRONTMATTER_DELIM:
        for i in range(1, len(lines)):
            if lines[i].strip() == FRONTMATTER_DELIM:
                start = i + 1
                break

    return _parse_simple_yaml(lines[start:])


def _parse_simple_yaml(lines: List[str]) -> Dict:
    """
    极简 YAML 解析器 — 只支持本项目用到的语法：
    - key: value
    - key: [a, b, c]   (inline list)
    - key: "quoted value"
    - key: number
    - 嵌套 dict: 通过缩进 (2 空格) 表达, 缩进层级形成嵌套
    - list of dict: 顶层 key 后面跟 '-' 行, 同一缩进

    V1.0 (V1.3.3 扩展): 支持嵌套 — default_accounts.yaml 用到
    """
    result = {}
    _parse_yaml_block(lines, 0, 0, result)
    return result


def _parse_yaml_block(lines: List[str], start: int, base_indent: int, out: Dict[str, Any]) -> int:
    """
    递归解析 YAML 块。
    返回: 处理到的行数 (从 start 起)
    """
    i = start
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # 计算缩进 (前导空格数)
        indent = len(line) - len(line.lstrip())

        # 缩进回到 base 或更小 → 本块结束
        if indent < base_indent:
            return i - start

        # 如果是 list item (以 '-' 开头)
        if stripped.startswith("- "):
            # list item 必须有父 key, 父 key 在外层
            # 当前块是 list, 我们期望父 key 已经创建
            return i - start

        # 解析 key: value (允许前导空格)
        m = re.match(r"^\s*([a-zA-Z_][\w-]*)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue

        key = m.group(1).strip()
        value = m.group(2).strip()
        i += 1

        if not value:
            # 可能是嵌套 dict 或 list
            # 找下一行 (跳过空行/注释) 的缩进
            j = i
            while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("#")):
                j += 1
            if j < len(lines):
                next_line = lines[j]
                next_stripped = next_line.strip()
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent > indent and next_stripped:
                    if next_stripped.startswith("- "):
                        # list of dict
                        lst = []
                        consumed = _parse_yaml_list(lines, j, next_indent, lst)
                        i = j + consumed
                        out[key] = lst
                    else:
                        # nested dict
                        nested: Dict[str, Any] = {}
                        consumed = _parse_yaml_block(lines, j, next_indent, nested)
                        i = j + consumed
                        out[key] = nested
                else:
                    out[key] = ""
            else:
                out[key] = ""
        else:
            out[key] = _coerce_value(value)


    return i - start


def _parse_yaml_list(lines: List[str], start: int, base_indent: int, out: List[Any]) -> int:
    """
    解析 list of dict / list of scalar。
    每行以 '- ' 开头, 后面跟 scalar 或 key: value 对 (一个或多个, 缩进比 '-' 大 2)。
    """
    i = start
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = len(line) - len(line.lstrip())
        # list item 必须 indent >= base_indent (跟 - 同行/更深)
        if indent < base_indent:
            return i - start
        # 离开 list 的条件: indent 回到 base 且不是 - 开头 (说明是新 block)
        if indent == base_indent and not stripped.startswith("- "):
            return i - start
        # indent == base 且是 - 开头: 继续, 是新 list item
        if indent < base_indent:
            return i - start
        if not stripped.startswith("- "):
            # inline 后续 (例如同一 item 的 account:), 跳过由具体处理逻辑
            # 但 list 主体认为"不是 list item", 应该 return 让 caller 知道 list 结束
            # 然而实际: 这种情况不应该出现在 list 主体 while 顶 (因为 item 处理完会调 inline 处理 inline 行)
            # 保留 return 防止无限循环
            return i - start

        # 解析 item 内容
        item_content = stripped[2:].strip()  # 去掉 "- "

        if not item_content:
            # '-' 后面空, 说明是 dict (下一行是 key: value, 缩进比当前行大 2)
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("#")):
                j += 1
            if j < len(lines):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                # 期望 next_indent >= base_indent + 2
                if next_indent >= base_indent + 2:
                    item = {}
                    consumed = _parse_yaml_block(lines, j, next_indent, item)
                    i = j + consumed
                    out.append(item)
                else:
                    out.append({})
                    i = j
            else:
                out.append({})
        elif ":" in item_content:
            # '- key: value' 形式, 一行 dict
            m = re.match(r"^\s*([a-zA-Z_][\w-]*)\s*:\s*(.*)$", item_content)
            if m:
                k = m.group(1).strip()
                v = m.group(2).strip()
                if not v:
                    # '- key:' 后面空, 期待嵌套 dict
                    # 整段处理: nested (缩进 > base+2) + inline 后续 (缩进 = base+2)
                    item: Dict[str, Any] = {k: {}}
                    i = i + 1  # 跳过 "- <k>:" 这一行
                    nested_done = False
                    while i < len(lines):
                        line = lines[i]
                        stripped = line.strip()
                        if not stripped or stripped.startswith("#"):
                            i += 1
                            continue
                        next_indent = len(line) - len(line.lstrip())
                        if next_indent < base_indent + 2:
                            # 回到 base 以下, 退出
                            break
                        if next_indent == base_indent + 2 and not stripped.startswith("- "):
                            # inline 后续 (跟 <k> 同行)
                            m2 = re.match(r"^\s*([a-zA-Z_][\w-]*)\s*:\s*(.*)$", line)
                            if m2:
                                k2 = m2.group(1).strip()
                                v2 = m2.group(2).strip()
                                if v2:
                                    item[k2] = _coerce_value(v2)
                                else:
                                    item[k2] = "" if not nested_done else ""
                            i += 1
                        elif next_indent > base_indent + 2 and not stripped.startswith("- "):
                            # nested 块
                            if not nested_done:
                                consumed = _parse_yaml_block(lines, i, next_indent, item[k])
                                i += consumed
                                nested_done = True
                            else:
                                # nested 已 done, 还在更深? 错误, 跳过
                                i += 1
                        elif next_indent == base_indent and stripped.startswith("- "):
                            # 新 list item, 退出
                            break
                        else:
                            i += 1
                    out.append(item)
                else:
                    item = {k: _coerce_value(v)}
                    # 后面可能还有更多 key: value (缩进比当前行大 2, 不以 - 开头)
                    i += 1
                    while i < len(lines):
                        next_line = lines[i]
                        next_stripped = next_line.strip()
                        if not next_stripped or next_stripped.startswith("#"):
                            i += 1
                            continue
                        next_indent = len(next_line) - len(next_line.lstrip())
                        # break 条件: indent 回到 base (或更小) 且不是 list item
                        if next_indent <= base_indent and not next_stripped.startswith("- "):
                            break
                        if next_indent <= base_indent and next_stripped.startswith("- "):
                            # 新 list item, 退出 inline 循环, 让 list 主体接住
                            break
                        m2 = re.match(r"^\s*([a-zA-Z_][\w-]*)\s*:\s*(.*)$", next_line)
                        if m2:
                            k2 = m2.group(1).strip()
                            v2 = m2.group(2).strip()
                            if not v2:
                                # 嵌套
                                if i + 1 < len(lines):
                                    nn = lines[i + 1]
                                    nn_indent = len(nn) - len(nn.lstrip())
                                    if nn_indent > next_indent and nn.strip():
                                        if nn.strip().startswith("- "):
                                            lst = []
                                            consumed = _parse_yaml_list(lines, i + 1, nn_indent, lst)
                                            item[k2] = lst
                                            i += 1 + consumed
                                            continue
                                        else:
                                            nested = {}
                                            consumed = _parse_yaml_block(lines, i + 1, nn_indent, nested)
                                            item[k2] = nested
                                            i += 1 + consumed
                                            continue
                                item[k2] = ""
                            else:
                                item[k2] = _coerce_value(v2)
                        i += 1
                    out.append(item)
        else:
            # '- scalar'
            out.append(_coerce_value(item_content))
            i += 1

    return i - start


def _coerce_value(raw: str):
    """把字符串值转成合适类型。"""
    if not raw:
        return ""

    # 去掉尾部注释 (# 后到行尾, 但不在引号内)
    # 简单处理: 找 " #" 或 "\t#" 模式 (前面有空格避免吃掉 # 字符)
    # 注: 不完美, 但够用
    cleaned = re.sub(r"\s+#.*$", "", raw).strip()
    if not cleaned:
        return ""

    # Inline list: [a, b, c]
    if cleaned.startswith("[") and cleaned.endswith("]"):
        inner = cleaned[1:-1].strip()
        if not inner:
            return []
        return [_coerce_value(x.strip()) for x in inner.split(",")]

    # Quoted string
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (
        cleaned.startswith("'") and cleaned.endswith("'")
    ):
        return cleaned[1:-1]

    # Boolean
    if cleaned.lower() == "true":
        return True
    if cleaned.lower() == "false":
        return False

    # Number
    try:
        if "." in cleaned:
            return float(cleaned)
        return int(cleaned)
    except ValueError:
        pass

    # Plain string
    return cleaned


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
