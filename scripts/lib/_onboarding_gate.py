"""
_onboarding_gate.py — Onboarding 守门检查 (V1.3.4)

当 Agent 帮用户配了 launchd / cron 定时任务, 但用户**还没**完成 Onboarding 时,
5 个定时脚本 (daily/credit/loan/installment/weekly_dashboard) 会因 vault 不完整
(账户表空 / 模板缺失) 而乱报 ERROR。

解决: 每个脚本 main() 开头调 is_initialized(vault_root), 未初始化就 INFO 跳过
而不是 ERROR 退出 (onboarding 期不吓用户, 也不写假告警)。

判定标准 (V1.3.4):
  - Accounts/account-list.md 存在
  - Accounts/agent-config.md 存在 (V1.0 起约定)
  - 账户表 frontmatter 至少 1 个账户

设计原则: 软告警 (按 AGENTS.md 偏好), 不强制 fail。
"""

import os
from typing import Tuple


def is_initialized(vault_root: str) -> Tuple[bool, str]:
    """
    检查 vault 是否已完成 Onboarding。

    Returns:
        (True, "OK")     — 已初始化, 正常跑
        (False, reason)  — 未初始化, reason 说明缺什么
    """
    if not vault_root or not os.path.isdir(vault_root):
        return False, f"vault 目录不存在: {vault_root}"

    account_list = os.path.join(vault_root, "Accounts", "account-list.md")
    if not os.path.isfile(account_list):
        return False, f"missing {account_list} (未完成 Onboarding 步骤 3)"

    agent_config = os.path.join(vault_root, "Accounts", "agent-config.md")
    if not os.path.isfile(agent_config):
        return False, f"missing {agent_config} (未完成 Onboarding 步骤 6)"

    # 检查账户表是否真有内容 (frontmatter + 至少 1 行账户)
    try:
        from lib.parsers import parse_accounts
        accounts = parse_accounts(vault_root)
    except Exception as e:
        return False, f"parse_accounts 失败: {e}"

    if not accounts:
        return False, "账户表为空 (frontmatter 没 accounts 或表格无行)"

    return True, "OK"


def gate_or_skip(vault_root: str, script_name: str) -> bool:
    """
    守门主入口: 已初始化返回 True, 未初始化打印 INFO 并返回 False。

    用法 (在 main() 开头):
        from lib._onboarding_gate import gate_or_skip
        if not gate_or_skip(args.vault, "daily_integrity_check.py"):
            return 0  # 软跳过
    """
    ok, reason = is_initialized(vault_root)
    if ok:
        return True

    # 未初始化: 打印 INFO (不写 alerts.md, 不 ERROR 退出)
    print(f"[INFO] {script_name}: 跳过 — {reason}")
    print(f"[INFO] 这是 Onboarding 期正常状态, 不是错误。")
    print(f"[INFO] 完成 Onboarding 后此脚本会正常运行 (见 zh/AGENTS-PROACTIVE.md 步骤 1-7)")
    return False
