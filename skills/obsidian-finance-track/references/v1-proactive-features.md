# V1 Proactive Features — 设计参考 (commit 5c10e67 + 6 新功能)

本文档归档 `obsidian-personal-finance-track` V1.0 主动化阶段的**设计决策**与**实现陷阱**。本节不重复 SKILL.md 的步骤说明, 而是讲**为什么这样设计**和**踩过的坑**。

---

## 1. 核心定位反转: Agent 是管家, 不是计算器

**旧定位** (V0.x): "Agent 只在用户开会话时在线, 校验靠 Agent 主动调, 不依赖 cron"
**新定位** (V1.0): "Agent 主动帮用户配 launchd/cron 定时任务, 用户复制粘贴即可"

### 为什么反转?

用户原话 (2026-06-01):
> "不是不让用户配定时任务, 是要 agent 主动引导或帮助用户去配, **只有定时任务才能让 agent 被唤醒来主动提醒用户**"

误读历史: 第一版 SKILL.md 写"Agent 主动调用脚本"——**字面没错**, 但实际暗示"不需要 cron, Agent 搞定一切"。问题是: **Agent 会话一关, 提醒就停了**——用户错过还款日/记账日都不知道。

### 正确产品形态

- **Onboarding 步骤 4**: Agent 主动问"要不要我帮你配以下定时任务?", 同时生成 plist/crontab 模板让用户复制粘贴
- **Onboarding 步骤 5**: 通知偏好——"校验失败时我用我自己的通道 (飞书/微信) 发给你, 还是写 alerts.md?"
- **用户复制粘贴 plist 后**: Agent 主动验证 `launchctl list` 看到任务已注册
- **会话内**: Agent 主动分析 alerts.md
- **会话外**: cron 跑脚本 → 写 alerts.md → 用户下次开会话看到

### 同步检查清单 (改动后必须查的)

每次改 `obsidian-finance-track` 相关文案, **同时检查 4 个文件**, 任何一处说"Agent 主动调, 不依赖 cron" 都要反向修正:

| 文件 | 章节 | 关键词 |
|------|------|--------|
| `~/.hermes/skills/productivity/obsidian-finance-track/SKILL.md` | Onboarding 步骤 4 + daily_integrity_check 段 | "Agent 自己在会话开始时判断" / "不依赖系统 cron" |
| `~/Project/obsidian-personal-finance-tracker/README.md` | 通知渠道段 + 脚本表 + 主动行为列表 | "用户不需要配定时任务" / "Agent 主动调用" |
| `~/Project/obsidian-personal-finance-tracker/zh/AGENTS-PROACTIVE.md` | 顶部对比表 + 末尾 cron 段 | "Agent 跑 daily check 不依赖系统 cron" |
| `~/Project/obsidian-personal-finance-tracker/en/AGENTS-PROACTIVE.md` | 同上英文版 | "Agent itself checks is it time" |

---

## 2. 6 个新功能 (用户选定 ROI 排序)

按"数据来源"分 A/B 两类:

### A 类 — 纯分析现有数据 (无新字段)

| # | 功能 | 文件 | 触发时机 |
|---|------|------|----------|
| 33 | 记账频率分析 | `scripts/daily_integrity_check.py::check_bookkeeping_frequency` | 每日 18:00 |
| 34 | 账户遗忘检测 | `scripts/daily_integrity_check.py::check_account_inactivity` | 每日 18:00 |
| 35 | 周末复盘 | `scripts/weekly_summary.py` (新建) | 每周日 20:00 |
| 36 | 月末自检 | `scripts/monthly_summary.py` (新建) | 每月最后一日 21:00 |

### B 类 — 需要新数据架构

| # | 功能 | 新增字段/文件 | 触发时机 |
|---|------|--------------|----------|
| 23 | 信用卡还款提醒 | `account-list.md` 表加 `账单日/还款日/信用额度` 4 字段 + `scripts/credit_card_reminder.py` | 每日 08:00 |
| 24 | 分期摊销追踪 | expense frontmatter 加 `is_installment/total_installments/installment_index/installment_group_id` + `scripts/installment_helper.py` (生成 N-1 PENDING 期) + `scripts/installment_check.py` (完整性检测) | 每日 08:05 |

---

## 3. 关键踩坑 — 给未来 session 留的警告

### 坑 A: 信用卡下次还款日跨月算法

```python
# 错误写法
next_due = today.replace(day=due_day)  # 当 due_day=5, today=6/1 → next_due=6/5 ✅
                                   # 当 due_day=5, today=6/8 → next_due=6/5 (过去!!) ❌

# 正确写法 (credit_card_reminder.py L43-58)
if today.day < due_day:
    next_due = today.replace(day=due_day)
else:
    # 跨到下月
    if today.month == 12:
        next_due = today.replace(year=today.year+1, month=1, day=due_day)
    else:
        next_due = today.replace(month=today.month+1, day=due_day)
```

**测试覆盖** 5 个场景:
1. due_day=15, today=6/1 → 14 天 (未来本月)
2. due_day=3, today=6/5 → 28 天 (跨月)
3. due_day=5, today=6/1 → 4 天 (≤5 天应 WARN)
4. due_day=5, today=6/10 → 25 天 (跨月)
5. due_day=2, today=12/15 → 18 天 (跨年)

### 坑 B: 分期 helper 文件名 bug (已修)

**问题**: 从第一期文件名 `2026-04-15-expense-iphone-500-CNY-ACTIVE.md` 推算其他期时, `base_name.split('-', 1)[1]` 把日期前缀当 title 拼回去, 输出 `2026-05-15-04-15-expense-iphone-500-...`

**修复** (commit 后续): 用正则 `r"^\d{4}-\d{2}-\d{2}-"` 剥日期前缀, 再 rsplit(3) 提取 `title/amount/currency`。
**注意**: rsplit 用 3 (从右数 3 段), 因为 status 是最后一段。

### 坑 C: parse_accounts 列顺序耦合 → 重构为列名匹配

**问题**: 原实现硬编码 3 列 `[账户, 币种, 初始余额]`, 加 #23 字段后变 8 列, 旧代码彻底失效。
**修复**: 重写为**按列名匹配** (header 行小写规范化后, 每列取名字), 不依赖列顺序。
**好处**: 以后再加字段 (例如 `#XX 贷款账户月供` 加 `loan_amount` `interest_rate`) 也不用改 parsers.py。

### 坑 D: INFO 级别被误判为 error

**问题**: #33 #34 会产生 INFO 级别告警 (不是真问题, 是审计信息), 但原 `if not all_errors` 判断把所有非空都当 error。
**修复**: 把 INFO 分支独立处理 — 即使无 error, 仍写一条 INFO 到 alerts.md (审计痕迹), 但 exit 0。

### 坑 E: 测试 vault 不能用 `--vault .`

**问题**: 项目仓库路径是 `~/Project/obsidian-personal-finance-tracker-v1.0-DRAFT/`, 仓库**有** `zh/` `en/` `scripts/`, 但**没有** `Transactions/Accounts/Dashboards/`。如果用 `--vault .` (项目根) 当 vault, validate_transaction 找不到账户表, 全部报错。
**修复**: 测试时用 `/tmp/test-vault/` 模拟真实 vault 结构 (`Accounts/` + `Transactions/{expenses,incomes,transfers/{out,in}}`), 不用项目仓库路径。

---

## 4. Onboarding 配置清单 (Agent 给用户生成时复制此模板)

### macOS launchd plist (放 `~/Library/LaunchAgents/`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lovepigpanda.finance-daily-integrity</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/你的用户名/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>18</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/finance-daily.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/finance-daily.err</string>
</dict>
</plist>
```

加载: `launchctl load ~/Library/LaunchAgents/com.lovepigpanda.finance-daily-integrity.plist`
验证: `launchctl list | grep finance-daily`

### Linux crontab

```cron
# 每日 18:00 跑守恒
0 18 * * * /usr/bin/python3 /home/你的用户名/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py >> /tmp/finance-daily.log 2>&1

# 每周日 20:00 跑周末复盘
0 20 * * 0 /usr/bin/python3 .../scripts/weekly_summary.py --vault ~/Obsidian/finance >> /tmp/finance-weekly.log 2>&1

# 每月最后一日 21:00 跑月末自检
0 21 28-31 * * [ "$(date +\%d -d tomorrow)" = "01" ] && /usr/bin/python3 .../scripts/monthly_summary.py --vault ~/Obsidian/finance
```

---

## 5. 复盘: 实施顺序建议 (避免重复劳动)

按以下顺序实施 6 功能可减少返工:

1. **A4**: #36 月末自检 (因为需要的字段最少, 几乎无 schema 变化)
2. **A3**: #35 周末复盘 (跟 #36 共用大部分 utilities)
3. **A1+A2**: #33 + #34 (一起加进 daily_integrity_check, 共享 transfer scan)
4. **B1**: #23 信用卡 (先改 account-list.md schema + parsers, 再写脚本)
5. **B2**: #24 分期 (helper + check 一起写, 因为 helper 输出格式决定 check 解析逻辑)
6. **文档同步**: 5 个新脚本到 README + SKILL.md + AGENTS-PROACTIVE.md (zh + en)
7. **集成测试**: 跑全部 6 个脚本在 /tmp/test-vault/ 上, 验证互不干扰
8. **commit + push + aweskill update + cp 到 ~/.hermes/skills/**

**不要**先改文档再改代码——文档改了但代码没改, 用户跑会报找不到脚本的错。
