# Obsidian Personal Finance Tracker

### 🤖 你的 AI 理财搭档 · Your AI Finance Partner

---

## 📦 安装 (V1.2.1 必读)

**所有定时任务都依赖仓库根的 `scripts/` 目录**（9 个 Python 脚本，零依赖）。

### 方式 A：完整 clone (推荐)

```bash
git clone https://github.com/lovepigpanda/obsidian-personal-finance-tracker.git ~/Project/obsidian-personal-finance-tracker
# 后续更新
cd ~/Project/obsidian-personal-finance-tracker && git pull
```

### 方式 B：用 aweskill 装技能 + 手动 cp scripts/

```bash
# 1. 装技能 (只同步 skills/ 目录)
aweskill install --skill obsidian-finance-track

# 2. 手动 cp scripts/ 到项目目录 (重要！aweskill 不同步仓库根 scripts/)
mkdir -p ~/Project/obsidian-personal-finance-tracker
cp ~/.aweskill/skills/obsidian-finance-track/scripts/*.py ~/Project/obsidian-personal-finance-tracker/scripts/

# 3. 后续更新
aweskill update obsidian-finance-track
# 注意: aweskill update 只更新 skills/, scripts/ 需要从 GitHub 重新 clone 或手动 cp
cd ~/Project/obsidian-personal-finance-tracker && git pull
```

**验证**：
```bash
ls ~/Project/obsidian-personal-finance-tracker/scripts/loan_payment_reminder.py
# 期望: 文件存在, 大小 ~9KB
```

### ⚠️ 为什么 scripts/ 不能靠 aweskill 同步？

`aweskill install/update` 设计上只同步 `skills/<skill-name>/` 子目录，**不同步**仓库根的 `scripts/`。这是 aweskill 的设计，不是 bug。

如果只用 aweskill 装技能、不 clone 仓库，**所有定时任务都会失败**（找不到 `loan_payment_reminder.py` 等脚本）。

---

## ⚠️ 数据存储架构 — 重要

**技能代码与账本数据完全分离：**

| 内容 | 位置 | 说明 |
|------|------|------|
| 🤖 **AI Agent 技能** | GitHub 仓库 `skills/obsidian-finance-track/` | `git pull` 同步更新 |
| 📋 **模板/规则/仪表盘** | GitHub 仓库 `zh/` 和 `en/` | `git pull` 同步更新 |
| 🐍 **校验脚本** | GitHub 仓库 `scripts/` | `git pull` 同步更新（零依赖） |
| 💰 **你的账本数据** | `~/Obsidian/finance/Transactions/` | **本地私有，永不上传** |

```
GitHub 仓库（技能代码，可分发）
├── skills/obsidian-finance-track/   ← AI Agent 技能（中英双版）
├── zh/                               ← 中文模板/规则/仪表盘
├── en/                               ← English templates/rules/dashboards
├── scripts/                          ← 🐍 内部一致性校验脚本
└── .gitignore                        ← 忽略 Transactions/

本地 Obsidian vault（账本数据，私有）
└── ~/Obsidian/finance/
    ├── Templates/                    ← 模板（从 GitHub 复制）
    ├── Categories/                   ← 分类规则（从 GitHub 复制）
    ├── Dashboards/                   ← 仪表盘（从 GitHub 复制；alerts.md 由校验脚本运行时生成，不入 Git）
    ├── Accounts/                     ← 账户列表
    └── Transactions/                 ← 💰 你的真实账本数据（不上传）
        ├── expenses/
        ├── incomes/
        └── transfers/
            ├── out/                  ← 转账出账文件
            └── in/                   ← 转账入账文件
```

**为什么这样设计？**
- GitHub 项目是"技能"，别人可以放心地用 `git pull` 更新，不必担心覆盖账本
- 你的账本数据永远在本地，不会上传到 GitHub
- 模板和规则可以从 GitHub 同步，但每笔交易记录绝对安全
- 校验脚本与账本数据也分离——脚本本身开源可审计，但只读 vault 内容

---

## ✨ 功能特点

### 核心记账
- ✅ **支出记录** — 金额/分类/账户/支付方式/备注
- ✅ **收入记录** — 金额/来源分类/账户/备注
- ✅ **转账记录** — 1 笔转账 = 2 个文件（out + in）配对追踪
- ✅ **多账户余额追踪** — 自动计算（初始余额 + 收入 - 支出 - 转出 + 转入）
- ✅ **多币种分别统计** — CNY/USD/EUR/HKD/JPY/GBP 分开显示，不折算
- ✅ **分类自动映射** — 输入关键词自动 suggest 分类

### 内部一致性校验 🐍
- ✅ **单笔校验** — AI Agent 写完每笔交易后**自动跑**（步骤 7.5，Agent 责任）
- ✅ **每日守恒** — Agent 自己在会话开始时判断跑不跑（不依赖系统 cron）
- ✅ **周度结构** — Dataview 仪表盘 vs Python 余额对照，Agent 周日主动跑
- ✅ **零依赖** — 纯 Python 3.8+ 标准库，所有平台/所有 AI Agent 可用
- ✅ **软告警** — 文件保留，AI Agent 询问用户怎么处理
- ✅ **多渠道通知** — alerts.md + 桌面通知（脚本负责），飞书/微信/邮件（Agent 自己的通道）

### 用户体验
- ✅ **月度汇总报告** — Dataview 自动生成
- ✅ **主仪表盘** — 本月余额/分类占比/趋势
- 🤖 **AI Agent 支持** — 自然语言记账，自动创建交易文件

### 路线图
- 📅 **多币种汇率自动获取**（v1.1）
- 🏦 **银行 API 自动同步**（v2.0）

---

## 🔁 转账功能

**1 笔转账 = 2 个文件**（out + in），用 `transfer_pair_id` 字段关联：

```yaml
# Transactions/transfers/out/2026-06-01-transfer-out-Alipay-to-CMB-5000-CNY-ACTIVE.md
type: transfer
date: 2026-06-01
amount: 5000
currency: CNY
category: Transfer
from_account: Alipay
to_account: CMB
transfer_pair_id: T-2026-06-01-abc123   # ⚠️ out 和 in 必须完全一致
status: ACTIVE
```

**关键规则**：`from_account` / `to_account` 在 out 和 in 两个文件**完全一致**（统一语义——表达"同一笔交易"），不是镜像。校验脚本会自动检查配对完整性。

**触发词**：转 / 转给 / 打给 / 调拨 / 还信用卡 / from X to Y / 充值 / 提现

详见 [zh/AGENTS.md 示例 5](zh/AGENTS.md) 和 [zh/Templates/transfer-template.md](zh/Templates/transfer-template.md)

---

## 🐍 内部一致性校验（scripts/）— Agent 主动调用

**为什么需要？** 用户只输入初始余额，所有加减都是项目自己处理——一旦内部计算错（转账配对丢失、字段填错），余额就不准了。校验脚本保证**项目自己算的不会错**。

**核心定位**: 脚本是**Agent 调用的工具**，**不是**独立服务。Agent 在合适的时候主动调脚本，**不**依赖系统 cron、**不**配 webhook——通知也由 Agent 用自己已有的通道主动推。

### 三个核心脚本

| 脚本 | Agent 何时调 | 校验内容 |
|------|------------|---------|
| `validate_transaction.py` | **每次记账后立即**（步骤 7.5，Agent 责任） | 必填字段、金额合法、日期合法、币种合法、账户已注册、**transfer 配对完整且一致** |
| `daily_integrity_check.py` | **Agent 帮用户配每日 18:00 定时任务** (launchd/cron) | 转账配对守恒、每币种 transfer 平衡、Python 余额 vs 累加自洽、透支检查、**#33 记账频率、#34 账户遗忘检测** |
| `weekly_dashboard_check.py` | **Agent 周日 8 点主动调** | 仪表盘文件结构、账户表完整、打印权威余额供对账 |
| `weekly_summary.py` | **Agent 周末 20 点主动调 (#35)** | 本周笔数 / 收支 / 分类前 3 / 同比上周，写 alerts.md |
| `monthly_summary.py` | **Agent 月末主动调 (#36)** | 本月笔数 / 收支 / 储蓄率 / 分类汇总 / 跨账户流量，写 alerts.md |
| `credit_card_reminder.py` | **Agent 帮用户配每日 8:00 定时任务 (#23)** | 信用卡还款日提醒 (WARN: ≤5 天, INFO: >5 天) |
| `installment_check.py` | **Agent 帮用户配每日 8:00 定时任务 (#24)** | 分期组完整性、字段一致性、PENDING 到期提醒 |
| `installment_helper.py` | **用户写完第一期 expense 时 Agent 调 (#24)** | 从第一期生成 N-1 个 PENDING 期模板 |
| `loan_payment_reminder.py` | **Agent 帮用户配每日 8:10 定时任务 (#37)** | 贷款月供提醒 (WARN: ≤5 天, ERROR: 已过未还, INFO: 已还) |

### 用法

```bash
# 单笔校验 (AI Agent 自动调用)
python3 ~/Project/obsidian-personal-finance-tracker/scripts/validate_transaction.py <新文件>

# 每日守恒
python3 ~/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py

# 周度结构
python3 ~/Project/obsidian-personal-finance-tracker/scripts/weekly_dashboard_check.py

# 周末复盘 (#35) - Agent 周日 20:00 主动调
python3 ~/Project/obsidian-personal-finance-tracker/scripts/weekly_summary.py --vault ~/Obsidian/finance

# 月末自检 (#36) - Agent 月末主动调
python3 ~/Project/obsidian-personal-finance-tracker/scripts/monthly_summary.py --vault ~/Obsidian/finance

# 信用卡还款提醒 (#23) - Agent 帮用户配每日 8:00 定时任务
python3 ~/Project/obsidian-personal-finance-tracker/scripts/credit_card_reminder.py --vault ~/Obsidian/finance

# 分期检查 (#24) - Agent 帮用户配每日 8:00 定时任务
python3 ~/Project/obsidian-personal-finance-tracker/scripts/installment_check.py --vault ~/Obsidian/finance

# 分期模板生成 (#24) - 用户写完第一期后, Agent 调
python3 ~/Project/obsidian-personal-finance-tracker/scripts/installment_helper.py create \
  --first-file ~/Obsidian/finance/Transactions/expenses/<第一期文件> \
  --total 12

# 贷款月供提醒 (#37) - Agent 帮用户配每日 8:10 定时任务
python3 ~/Project/obsidian-personal-finance-tracker/scripts/loan_payment_reminder.py --vault ~/Obsidian/finance
```

### 通知渠道

**脚本只做最基础的**（无需配置）：

1. **`~/Obsidian/finance/Dashboards/alerts.md`** — 始终写入，在 Obsidian 里看
2. **桌面通知** — macOS `osascript` / Linux `notify-send`

**其他渠道（飞书 / 微信 / 邮件 / 短信）由 Agent 负责**——Agent 用自己已有的消息通道主动推。详见 [zh/AGENTS-PROACTIVE.md](zh/AGENTS-PROACTIVE.md)。

> **关键设计**：校验脚本不依赖系统 cron / launchd / GitHub Actions——**全部由 Agent 主动调用**。用户**不需要**配定时任务，那是 Agent 的事。

---

## 🤖 AI Agent 使用

本系统主要面向 **AI Agent**（Claude / Hermes / OpenClaw / Claude Code / Cursor 等），用户用自然语言描述交易，AI Agent 自动：

1. 解析意图（支出/收入/**转账**）、日期、金额、币种
2. 匹配账户和分类（根据 `QUICK-REFERENCE.md` 映射表）
3. 在 `~/Obsidian/finance/Transactions/` 下创建对应 `.md` 文件
4. **自动跑校验脚本**（步骤 7.5）保证数据一致性

**示例：**

用户 → `"午餐沙县花了45元，支付宝付款"`
AI Agent → 创建文件 + 跑校验 ✓

用户 → `"从支付宝转 5000 到招行，还信用卡"`
AI Agent → 创建 2 个 transfer 文件（共 pair_id）+ 跑校验 2 次 ✓

详见：[zh/AGENTS.md](zh/AGENTS.md) · [zh/QUICK-REFERENCE.md](zh/QUICK-REFERENCE.md) · [en/AGENTS.md](en/AGENTS.md)

---

## 📁 项目结构

```
obsidian-personal-finance-tracker/        ← GitHub 仓库（技能代码）
├── skills/obsidian-finance-track/        ← 🤖 AI Agent 技能（中英双版 SKILL.md）
├── zh/                                   # 🌏 中文版
│   ├── AGENTS.md                         # AI Agent 使用指南
│   ├── AGENTS-PROACTIVE.md               # Agent 主动行为指南（Onboarding + 周期检查 + 主动建议）
│   ├── QUICK-REFERENCE.md                # 快速参考
│   ├── Templates/                        # 模板文件（expense/income/transfer）
│   ├── Dashboards/                       # Dataview 仪表盘 + alerts.md
│   ├── Accounts/                         # 账户列表
│   └── Categories/                       # 分类规则
├── en/                                   # 🌎 English version (mirror of zh/)
├── scripts/                              # 🐍 内部一致性校验脚本
│   ├── validate_transaction.py           # 单笔校验（步骤 7.5）
│   ├── daily_integrity_check.py          # 每日守恒
│   ├── weekly_dashboard_check.py         # 周度结构
│   └── lib/                              # 共享库（零依赖）
│       ├── parsers.py                    # frontmatter 解析、转账配对
│       ├── balance.py                    # 余额计算核心
│       └── notifier.py                   # 通知分发
└── .gitignore                            # 忽略 Transactions/ 和 __pycache__/
```

---

## 🚀 快速开始

### AI Agent 接入（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/lovepigpanda/obsidian-personal-finance-tracker.git ~/Project/obsidian-personal-finance-tracker

# 2. 在 Obsidian vault 创建账本目录
mkdir -p ~/Obsidian/finance/{Templates,Categories,Dashboards,Accounts,Transactions/{expenses,incomes,transfers/{out,in}}}

# 3. 复制模板和规则（从 GitHub 到本地 vault）
cp ~/Project/obsidian-personal-finance-tracker/zh/Templates/*.md ~/Obsidian/finance/Templates/
cp ~/Project/obsidian-personal-finance-tracker/zh/Categories/*.md ~/Obsidian/finance/Categories/
cp ~/Project/obsidian-personal-finance-tracker/zh/Dashboards/*.md ~/Obsidian/finance/Dashboards/
cp ~/Project/obsidian-personal-finance-tracker/zh/Accounts/*.md ~/Obsidian/finance/Accounts/

# 4. 安装 AI Agent 技能
aweskill install https://github.com/lovepigpanda/obsidian-personal-finance-tracker
aweskill agent add --agent openclaw skill obsidian-finance-track
aweskill agent add --agent claude-code skill obsidian-finance-track
```

### 人类手动录入

1. 在 Obsidian 中安装 **Dataview** 和 **Templater** 插件
2. 复制 `zh/Templates/`、`zh/Dashboards/`、`zh/Accounts/`、`zh/Categories/` 到 `~/Obsidian/finance/`
3. Templater → 新建笔记 → 选择 `expense-template.md` / `income-template.md` / `transfer-template.md`
4. 打开 `~/Obsidian/finance/Dashboards/finance-dashboard.md` 查看财务概况
5. 校验异常会在 `~/Obsidian/finance/Dashboards/alerts.md` 显示

### 🤖 Agent 主动行为 (Onboarding + 周期检查 + 主动建议)

**这个项目的核心定位**：所有用户都有 AI Agent，所以 Agent **不是计算器，是管家**。

用户装好技能后，Agent 会在第一次会话主动引导完整 7 步 Onboarding（确认 vault、引导填账户、配置校验策略、配置通知偏好等），结果存到 `~/Obsidian/finance/Accounts/agent-config.md`。

之后 Agent 会：
- **每次会话开始**主动检查 vault 健康
- **每次记账后**自动跑 `validate_transaction.py`（步骤 7.5）
- **每日**主动跑 `daily_integrity_check.py`（不依赖系统 cron，Agent 自己判断"该跑了吗"）
- **每周日**主动跑 `weekly_dashboard_check.py` 并总结本周财务
- **每月 1 号**主动给上月总结 + 预算建议
- **校验失败**时用 Agent 自己的通道（飞书/微信/邮件）主动推给用户

**不要**让用户去配 cron / launchd / GitHub Actions / webhook / Bark key——那都是 Agent 的事。

完整行为规则见 [zh/AGENTS-PROACTIVE.md](zh/AGENTS-PROACTIVE.md)（英文：[en/AGENTS-PROACTIVE.md](en/AGENTS-PROACTIVE.md)）。

---

## 🛠️ 插件依赖

| 插件 | 必须 | 说明 |
|------|------|------|
| Dataview | ✅ | 查询和渲染仪表盘 |
| Templater | ✅ | 交互式录入模板（人类使用） |
| Commander | ❌ | 快捷命令（可选） |
| Obsidian Charts | ❌ | 趋势图展示（可选） |

**Python 依赖**（校验脚本）：**零**——只使用 Python 3.8+ 标准库。

---

## ⚠️ 已知限制

1. 多币种汇率需要手动维护（v1.1 计划自动获取）
2. 账户余额由 Python + Dataview 实时计算，初始余额需在 `Accounts/account-list.md` 中手动设置
3. 国内银行 API 暂不支持，自动同步功能延后（v2.0）
4. 校验脚本是**内部一致性**检查（保证项目自己算的没错），**不**对接银行真余额
5. `scripts/` 里的 `lib/` 用了 Python 3.8+ 的特性（f-string, type hints），不支持更老版本

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

主要可贡献方向：
- 增加新的校验规则（`scripts/lib/`）
- 适配更多 AI Agent 框架
- 多语言翻译（zh/en 已完成，欢迎其他语言）
- 新增功能（Dataloom 视图、移动端优化等）
- **Agent 主动策略**（[AGENTS-PROACTIVE.md](zh/AGENTS-PROACTIVE.md)）—— 贡献新场景、新触发器、新建议规则

---

## 📄 License

MIT License

---

***

<a name="english"></a>

# Obsidian Personal Finance Tracker

### 🤖 你的 AI 理财搭档 · Your AI Finance Partner

> [简体中文](#) | [English](#english)

---

## ⚠️ Data Storage Architecture — Important

**Skill code and ledger data are completely separated:**

| Content | Location | Notes |
|---------|----------|-------|
| 🤖 **AI Agent skill** | GitHub repo `skills/obsidian-finance-track/` | `git pull` to update |
| 📋 **Templates/rules/dashboards** | GitHub repo `zh/` and `en/` | `git pull` to update |
| 🐍 **Validation scripts** | GitHub repo `scripts/` | `git pull` to update (zero-dep) |
| 💰 **Your ledger data** | `~/Obsidian/finance/Transactions/` | **Local only, never upload** |

```
GitHub repo (skill code, shareable)
├── skills/obsidian-finance-track/   ← AI Agent skill (zh + en)
├── zh/                              ← Chinese templates/rules/dashboards
├── en/                              ← English templates/rules/dashboards
├── scripts/                         ← 🐍 Internal consistency validation
└── .gitignore                       ← Ignores Transactions/

Local Obsidian vault (ledger data, private)
└── ~/Obsidian/finance/
    ├── Templates/                    ← Templates (copy from GitHub)
    ├── Categories/                   ← Category rules (copy from GitHub)
    ├── Dashboards/                   ← Dashboards (from GitHub; alerts.md is generated by validation scripts at runtime, not in Git)
    ├── Accounts/                     ← Account list
    └── Transactions/                 ← 💰 Your real ledger data (never upload)
        ├── expenses/
        ├── incomes/
        └── transfers/
            ├── out/                  ← Transfer OUT files
            └── in/                   ← Transfer IN files
```

**Why this design?**
- GitHub repo is the "skill" — others can safely `git pull` to update without touching their ledger
- Your ledger data stays local, never uploaded to GitHub
- Templates and rules sync from GitHub, but every transaction record is safe
- Validation scripts are also separated from ledger data — scripts are open-source and auditable, only read vault contents

---

## ✨ Features

### Core Accounting
- ✅ **Expense tracking** — amount / category / account / payment method / note
- ✅ **Income tracking** — amount / source category / account / note
- ✅ **Transfer tracking** — 1 transfer = 2 files (out + in) paired via ID
- ✅ **Multi-account balance tracking** — auto-calculated (initial + income − expense − transfer_out + transfer_in)
- ✅ **Multi-currency separate display** — CNY / USD / EUR / HKD / JPY / GBP shown separately, no conversion
- ✅ **Automatic category mapping** — keyword input auto-suggests categories

### Internal Consistency Validation 🐍
- ✅ **Per-transaction validation** — AI Agent runs **immediately after each write** (Step 7.5, Agent's responsibility)
- ✅ **Daily conservation check** — Agent itself decides at session start whether to run (no system cron)
- ✅ **Weekly structure check** — Dataview dashboard vs Python balance cross-check, Agent proactively runs on Sundays
- ✅ **Zero dependencies** — pure Python 3.8+ standard library, works on all platforms / all AI Agents
- ✅ **Soft alerts** — files preserved, AI Agent asks user how to handle
- ✅ **Multi-channel notifications** — alerts.md + desktop notifications (scripts), Feishu / WeChat / email (Agent's own channel)

### User Experience
- ✅ **Monthly summary reports** — auto-generated via Dataview
- ✅ **Main dashboard** — monthly balance / category breakdown / trends
- 🤖 **AI Agent support** — natural language accounting, auto-creates transaction files

### Roadmap
- 📅 **Multi-currency exchange auto-fetch** (v1.1)
- 🏦 **Bank API auto-sync** (v2.0)

---

## 🔁 Transfer Feature

**1 transfer = 2 files** (out + in), linked by `transfer_pair_id`:

```yaml
# Transactions/transfers/out/2026-06-01-transfer-out-Alipay-to-CMB-5000-CNY-ACTIVE.md
type: transfer
date: 2026-06-01
amount: 5000
currency: CNY
category: Transfer
from_account: Alipay
to_account: CMB
transfer_pair_id: T-2026-06-01-abc123   # ⚠️ out and in must be IDENTICAL
status: ACTIVE
```

**Key rule**: `from_account` / `to_account` are **identical** in both out and in files (unified semantics — expressing "the same transaction"), NOT mirrored. The validation script automatically checks pair completeness.

**Trigger words**: 转 / 转给 / 打给 / 调拨 / 还信用卡 / from X to Y / 充值 / 提现

See [en/AGENTS.md Example 5](en/AGENTS.md) and [en/Templates/transfer-template.md](en/Templates/transfer-template.md)

---

## 🐍 Internal Consistency Validation (scripts/)

**Why?** The user only inputs initial balances; all subsequent additions/subtractions are handled by the project. If internal calculation breaks (transfer pair missing, field errors), balance becomes wrong. The validation scripts guarantee **the project's own calculation never fails**.

### Three Core Scripts

| Script | When | Validates |
|--------|------|-----------|
| `validate_transaction.py` | AI Agent calls after each write | Required fields, valid amount, valid date, valid currency, account registered, **transfer pair complete & consistent** |
| `daily_integrity_check.py` | **Agent helps user configure daily 18:00 scheduled task** (launchd/cron) | Transfer pair integrity, per-currency transfer balance, Python balance vs accumulation self-consistency, overdraft check, **#33 bookkeeping frequency, #34 account inactivity detection** |
| `weekly_dashboard_check.py` | Agent proactively runs on Sundays | Dashboard file structure, account table completeness, prints authoritative balances for cross-check |
| `weekly_summary.py` | **Agent proactively runs on Sunday 20:00 (#35)** | Weekly transactions / income / expense / top 3 categories / WoW change, writes to alerts.md |
| `monthly_summary.py` | **Agent proactively runs at month-end (#36)** | Monthly transactions / income / expense / savings rate / category breakdown / cross-account flow, writes to alerts.md |
| `credit_card_reminder.py` | **Agent helps user configure daily 8:00 scheduled task (#23)** | Credit card payment reminder (WARN: ≤5 days, INFO: >5 days) |
| `installment_check.py` | **Agent helps user configure daily 8:00 scheduled task (#24)** | Installment group integrity, field consistency, PENDING-due reminder |
| `installment_helper.py` | **Agent calls after user writes first installment (#24)** | Generate N-1 PENDING installment templates from first |
| `loan_payment_reminder.py` | **Agent helps user configure daily 8:10 scheduled task (#37)** | Loan payment reminder (WARN: ≤5 days, ERROR: overdue, INFO: paid) |

### Usage

```bash
# Per-transaction validation (AI Agent auto-calls)
python3 ~/Project/obsidian-personal-finance-tracker/scripts/validate_transaction.py <new_file>

# Daily conservation
python3 ~/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py

# Weekly structure
python3 ~/Project/obsidian-personal-finance-tracker/scripts/weekly_dashboard_check.py

# Weekly summary (#35) - Agent runs Sunday 20:00
python3 ~/Project/obsidian-personal-finance-tracker/scripts/weekly_summary.py --vault ~/Obsidian/finance

# Monthly summary (#36) - Agent runs at month-end
python3 ~/Project/obsidian-personal-finance-tracker/scripts/monthly_summary.py --vault ~/Obsidian/finance

# Credit card reminder (#23) - Agent helps user configure daily 8:00 scheduled task
python3 ~/Project/obsidian-personal-finance-tracker/scripts/credit_card_reminder.py --vault ~/Obsidian/finance

# Installment check (#24) - Agent helps user configure daily 8:00 scheduled task
python3 ~/Project/obsidian-personal-finance-tracker/scripts/installment_check.py --vault ~/Obsidian/finance

# Installment helper (#24) - After user writes first installment, Agent calls
python3 ~/Project/obsidian-personal-finance-tracker/scripts/installment_helper.py create \
  --first-file ~/Obsidian/finance/Transactions/expenses/<first_installment> \
  --total 12

# Loan payment reminder (#37) - Agent helps user configure daily 8:10 scheduled task
python3 ~/Project/obsidian-personal-finance-tracker/scripts/loan_payment_reminder.py --vault ~/Obsidian/finance
```

### Notification Channels

**Scripts do only the basics** (no configuration needed):

1. **`~/Obsidian/finance/Dashboards/alerts.md`** — always written, view in Obsidian
2. **Desktop notifications** — macOS `osascript` / Linux `notify-send`

**Other channels (Feishu / WeChat / email / SMS) are the Agent's responsibility** — Agent uses its own existing messaging channel to push. See [en/AGENTS-PROACTIVE.md](en/AGENTS-PROACTIVE.md).

> **Key design**: validation scripts do NOT depend on system cron / launchd / GitHub Actions — **all invoked proactively by the Agent**. Users **do NOT** need to configure scheduled tasks — that's the Agent's job.

---

## 🤖 AI Agent Usage

Designed for **AI Agents** (Claude / Hermes / OpenClaw / Claude Code / Cursor / etc.). The user describes a transaction in natural language, and the AI Agent automatically:

1. Parses intent (expense / income / **transfer**), date, amount, currency
2. Matches account and category (using `QUICK-REFERENCE.md` mapping tables)
3. Creates the corresponding `.md` file under `~/Obsidian/finance/Transactions/`
4. **Auto-runs validation script** (Step 7.5) to ensure consistency

**Example:**

User → `"Lunch at Shaxian spent 45 CNY, paid via Alipay"`
AI Agent → Create file + run validation ✓

User → `"Transfer 5000 from Alipay to CMB for credit card payment"`
AI Agent → Create 2 transfer files (shared pair_id) + run validation twice ✓

See: [en/AGENTS.md](en/AGENTS.md) · [en/QUICK-REFERENCE.md](en/QUICK-REFERENCE.md) · [zh/AGENTS.md](zh/AGENTS.md)

---

## 📁 Project Structure

```
obsidian-personal-finance-tracker/        ← GitHub repo (skill code)
├── skills/obsidian-finance-track/        ← 🤖 AI Agent skill (zh + en SKILL.md)
├── zh/                                   # 🌏 Chinese version
│   ├── AGENTS.md                         # AI Agent guide
│   ├── AGENTS-PROACTIVE.md               # Agent proactive behavior guide (Onboarding + periodic checks + proactive suggestions)
│   ├── QUICK-REFERENCE.md                # Quick reference
│   ├── Templates/                        # Templates (expense/income/transfer)
│   ├── Dashboards/                       # Dataview dashboards + alerts.md
│   ├── Accounts/                         # Account list
│   └── Categories/                       # Category rules
├── en/                                   # 🌎 English version (mirror of zh/)
├── scripts/                              # 🐍 Internal consistency validation
│   ├── validate_transaction.py           # Per-transaction (Step 7.5)
│   ├── daily_integrity_check.py          # Daily conservation
│   ├── weekly_dashboard_check.py         # Weekly structure
│   └── lib/                              # Shared lib (zero-dep)
│       ├── parsers.py                    # Frontmatter parser, transfer pairing
│       ├── balance.py                    # Balance calculation core
│       └── notifier.py                   # Notification dispatcher
└── .gitignore                            # Ignores Transactions/ and __pycache__/
```

---

## 🚀 Quick Start

### AI Agent Integration (Recommended)

```bash
# 1. Clone the project
git clone https://github.com/lovepigpanda/obsidian-personal-finance-tracker.git ~/Project/obsidian-personal-finance-tracker

# 2. Create ledger directory in Obsidian vault
mkdir -p ~/Obsidian/finance/{Templates,Categories,Dashboards,Accounts,Transactions/{expenses,incomes,transfers/{out,in}}}

# 3. Copy templates and rules (from GitHub to local vault)
cp ~/Project/obsidian-personal-finance-tracker/zh/Templates/*.md ~/Obsidian/finance/Templates/
cp ~/Project/obsidian-personal-finance-tracker/zh/Categories/*.md ~/Obsidian/finance/Categories/
cp ~/Project/obsidian-personal-finance-tracker/zh/Dashboards/*.md ~/Obsidian/finance/Dashboards/
cp ~/Project/obsidian-personal-finance-tracker/zh/Accounts/*.md ~/Obsidian/finance/Accounts/

# 4. Install AI Agent skill
aweskill install https://github.com/lovepigpanda/obsidian-personal-finance-tracker
aweskill agent add --agent openclaw skill obsidian-finance-track
aweskill agent add --agent claude-code skill obsidian-finance-track
```

### Manual Human Entry

1. Install **Dataview** and **Templater** plugins in Obsidian
2. Copy `zh/Templates/`, `zh/Dashboards/`, `zh/Accounts/`, `zh/Categories/` to `~/Obsidian/finance/`
3. Templater → New Note → select `expense-template.md` / `income-template.md` / `transfer-template.md`
4. Open `~/Obsidian/finance/Dashboards/finance-dashboard.md` to view financial overview
5. Validation alerts appear in `~/Obsidian/finance/Dashboards/alerts.md`

### 🤖 Agent Proactive Behavior (Onboarding + Periodic Checks + Proactive Suggestions)

**Core positioning of this project**: every user has an AI Agent, so the Agent is **not a calculator — it's a butler**.

After the user installs the skill, the Agent guides them through a complete 7-step Onboarding at the first session (confirm vault, fill account list, configure validation strategy, configure notification preferences, etc.), saving results to `~/Obsidian/finance/Accounts/agent-config.md`.

After that, the Agent will:
- **Every session start** — proactively check vault health
- **After every transaction** — auto-run `validate_transaction.py` (Step 7.5)
- **Daily** — proactively run `daily_integrity_check.py` (no system cron dependency — Agent itself checks "is it time?")
- **Every Sunday** — proactively run `weekly_dashboard_check.py` and summarize the week
- **First of each month** — proactively deliver last month's summary + budget suggestions
- **On validation failure** — push to user via Agent's own channel (Feishu / WeChat / email)

**Do NOT** ask the user to configure cron / launchd / GitHub Actions / webhooks / Bark keys — that's the Agent's job.

For complete behavior rules see [en/AGENTS-PROACTIVE.md](en/AGENTS-PROACTIVE.md) (中文：[zh/AGENTS-PROACTIVE.md](zh/AGENTS-PROACTIVE.md)).

---

## 🛠️ Plugin Dependencies

| Plugin | Required | Note |
|--------|----------|------|
| Dataview | ✅ | Query & render dashboards |
| Templater | ✅ | Interactive entry templates (human use) |
| Commander | ❌ | Quick commands (optional) |
| Obsidian Charts | ❌ | Trend charts (optional) |

**Python dependencies** (validation scripts): **NONE** — Python 3.8+ standard library only.

---

## ⚠️ Known Limitations

1. Multi-currency exchange rates require manual maintenance (v1.1 plans auto-fetch)
2. Account balances are calculated in real-time by Python + Dataview; initial balances must be set in `Accounts/account-list.md`
3. China bank APIs not yet supported; auto-sync deferred (v2.0)
4. Validation scripts check **internal consistency** (project's own calculation correctness) — they do **NOT** reconcile against real bank balances
5. `scripts/lib/` uses Python 3.8+ features (f-strings, type hints); older Python versions unsupported

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

Main contribution directions:
- Add new validation rules (`scripts/lib/`)
- Adapt to more AI Agent frameworks
- Translations (zh/en done — other languages welcome)
- New features (Dataloom views, mobile optimization, etc.)

---

## 📄 License

MIT License
