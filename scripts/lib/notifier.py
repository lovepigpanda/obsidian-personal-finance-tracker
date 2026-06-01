"""
notifier.py - 通知分发

支持：
1. alerts.md (默认开启) - 写入 ~/Obsidian/finance/Dashboards/alerts.md
2. 桌面通知 (默认开启) - macOS 用 osascript，Linux 用 notify-send
3. Webhook 推送 (可选) - 读环境变量，支持 Bark / PushPlus / Server酱 / 通用 webhook

所有通知渠道都是 best-effort，单个失败不影响其他。
"""

import json
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


def send_webhook(title: str, body: str) -> bool:
    """
    通过环境变量配置 Webhook 推送。
    优先尝试的 webhook 服务 (按顺序):
    1. OBSIDIAN_FINANCE_WEBHOOK_URL (通用)
    2. BARK_URL + BARK_KEY (Bark, iOS)
    3. PUSHPLUS_TOKEN (PushPlus, 微信推送)
    4. SCT_KEY (Server酱, 微信推送)

    返回是否成功。
    """
    url = os.environ.get("OBSIDIAN_FINANCE_WEBHOOK_URL")
    if url:
        return _post_json(url, {"title": title, "body": body})

    # Bark: https://api.day.app/{key}/{title}/{body}
    bark_key = os.environ.get("BARK_KEY")
    if bark_key:
        bark_url = (
            os.environ.get("BARK_URL", "https://api.day.app")
            + f"/{bark_key}/{title}/{body}"
        )
        return _http_get(bark_url)

    # PushPlus: http://www.pushplus.plus/send
    pushplus = os.environ.get("PUSHPLUS_TOKEN")
    if pushplus:
        return _post_json(
            "https://www.pushplus.plus/send",
            {"token": pushplus, "title": title, "content": body},
        )

    # Server酱: https://sctapi.ftqq.com/{key}.send
    sct = os.environ.get("SCT_KEY")
    if sct:
        return _post_json(
            f"https://sctapi.ftqq.com/{sct}.send",
            {"title": title, "desp": body},
        )

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
    统一通知入口: alerts.md + 桌面 + webhook (如有)。
    """
    # 1. alerts.md (always)
    write_alert(vault_root, title, severity, details or [body], source)

    # 2. 桌面通知
    send_desktop_notification(title, body)

    # 3. Webhook (可选)
    send_webhook(title, body)


def _which(cmd: str) -> bool:
    """检查命令是否存在。"""
    for p in os.environ.get("PATH", "").split(":"):
        if os.path.isfile(os.path.join(p, cmd)):
            return True
    return False


def _post_json(url: str, payload: dict) -> bool:
    """urllib 兜底 POST JSON,不依赖 requests。"""
    try:
        from urllib.request import Request, urlopen
        from urllib.error import URLError

        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except (URLError, TimeoutError, ValueError):
        return False


def _http_get(url: str) -> bool:
    """GET 请求 (Bark 用)。"""
    try:
        from urllib.request import urlopen
        from urllib.error import URLError

        with urlopen(url, timeout=10) as resp:
            return 200 <= resp.status < 300
    except (URLError, TimeoutError, ValueError):
        return False
