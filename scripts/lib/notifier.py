"""
notifier.py - 通知分发 (基础版)

支持:
1. alerts.md (默认开启) - 写入 ~/Obsidian/finance/Dashboards/alerts.md
2. 桌面通知 (默认开启) - macOS 用 osascript，Linux 用 notify-send

【设计原则】Webhook / 飞书 / 微信 / 邮件等通知**不**在脚本负责范围。
校验脚本只做最基础的、零配置的渠道。
其他渠道由 AI Agent 主动用自己已有的消息通道推送 (见 AGENTS-PROACTIVE.md)。

所有通知渠道都是 best-effort，单个失败不影响其他。
"""

import os
import platform
import subprocess
import sys
from datetime import datetime
from typing import List, Optional


def get_alerts_path(vault_root: str) -> str:
    return os.path.join(vault_root, "Dashboards", "alerts.md")


def write_alert(
    vault_root: str,
    title: str,
    severity: str,
    details: List[str],
    source: str = "",
) -> None:
    """
    追加一条告警到 alerts.md。

    severity: "INFO" | "WARN" | "ERROR"
    """
    alerts_path = get_alerts_path(vault_root)
    os.makedirs(os.path.dirname(alerts_path), exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = {"INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌"}.get(severity, "•")

    entry_lines = [
        "",
        f"## {emoji} {title}",
        f"- **时间**: {timestamp}",
        f"- **严重程度**: {severity}",
    ]
    if source:
        entry_lines.append(f"- **来源**: {source}")
    entry_lines.append("- **详情**:")
    for d in details:
        entry_lines.append(f"  - {d}")
    entry_lines.append("")

    entry = "\n".join(entry_lines)

    # 如果文件不存在,加 frontmatter + 标题
    if not os.path.exists(alerts_path):
        header = (
            "---\n"
            "title: 财务系统告警日志\n"
            "type: alerts\n"
            "created: " + timestamp.split()[0] + "\n"
            "version: V1.0\n"
            "status: ACTIVE\n"
            "---\n\n"
            "# 财务系统告警日志 (Alerts Log)\n\n"
            "> 此文件由 scripts/ 自动生成和维护,记录所有校验异常。\n"
            "> **不要手动删除告警条目** — 它们是项目内部一致性的审计痕迹。\n"
            "\n---\n"
        )
        with open(alerts_path, "w", encoding="utf-8") as f:
            f.write(header)

    with open(alerts_path, "a", encoding="utf-8") as f:
        f.write(entry)


def send_desktop_notification(title: str, body: str) -> bool:
    """
    发送桌面通知。返回是否成功。
    macOS: osascript; Linux: notify-send; Windows: 跳过。
    """
    system = platform.system()
    try:
        if system == "Darwin":
            # 转义双引号
            esc_title = title.replace('"', '\\"')
            esc_body = body.replace('"', '\\"')
            script = f'display notification "{esc_body}" with title "{esc_title}"'
            subprocess.run(
                ["osascript", "-e", script],
                check=True,
                timeout=5,
                capture_output=True,
            )
            return True
        elif system == "Linux":
            if _which("notify-send"):
                subprocess.run(
                    ["notify-send", title, body],
                    check=True,
                    timeout=5,
                    capture_output=True,
                )
                return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False
    return False


def notify(
    vault_root: str,
    title: str,
    body: str,
    severity: str = "WARN",
    details: Optional[List[str]] = None,
    source: str = "",
) -> None:
    """
    统一通知入口: alerts.md + 桌面通知。

    设计原则: 通知由 AI Agent 负责, 脚本只做最基础的本地通知。
    - alerts.md: 写入 vault, 供用户和 Agent 在 Obsidian 中查看
    - 桌面通知: macOS / Linux 弹出系统通知

    其他渠道 (飞书 / 微信 / 邮件) 由 Agent 用自己已有的通道主动推送,
    见 AGENTS-PROACTIVE.md。
    """
    # 1. alerts.md (always)
    write_alert(vault_root, title, severity, details or [body], source)

    # 2. 桌面通知
    send_desktop_notification(title, body)


def _which(cmd: str) -> bool:
    """检查命令是否存在。"""
    for p in os.environ.get("PATH", "").split(":"):
        if os.path.isfile(os.path.join(p, cmd)):
            return True
    return False
