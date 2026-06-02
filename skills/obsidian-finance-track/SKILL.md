---
name: obsidian-finance-track
tagline: 你的 AI 理财搭档 · Your AI Finance Partner
description: >
  Obsidian 个人财务追踪 AI Agent Skill。当用户描述记账相关的内容（支出、收入、转账、钱包余额、工资、消费等）时，
  或明确说"记账"、"记一笔"、"花了多少"、"收到"、"转给 X"等触发词时，加载此 Skill。

  支持中文和英文用户，自动解析自然语言输入，在 Obsidian vault 中创建交易 md 文件，并更新 Dataview 仪表盘。

  ⚠️ 技能代码与账本数据分离：技能来自 GitHub 同步，账本数据存本地 ~/Obsidian/finance/
  详见「数据存储架构」章节。

  🚨 首次加载强制入口：当用户说"装好了"/"开始用"/"设置记账"/"初始化"等关键词，
  或 vault 目录缺少 `Accounts/agent-config.md` 时，**必须**立即执行「Onboarding 7 步」，
  不能直接进入记账流程。未完成 Onboarding = 未真正启用本技能。
triggers:
  # === 初始化触发词（首次使用）===
  - 装好了
  - 开始用
  - 初始化
  - 设置记账
  - 配置记账
  - onboard
  - setup
  - initialize
  # === 记账触发词 ===
  - 记账
  - 记一笔
  - 花了
  - 买了
  - 支出
  - 收入
  - 收到钱
  - 工资
  - 消费
  - 转账
  - 转给
  - 转到
  - 打给
  - 还信用卡
  - 调拨
  - 充值
  - 提现
  - expense
  - income
  - transfer
  - spent
  - paid
  - received
  - 午餐
  - 晚餐
  - 支付宝
  - 微信支付
  - 银行卡
  - 报销
  - 退款
  - 红包
  - balance
  - 余额
  - 账户
version: V1.2
status: ACTIVE
tags: [finance, obsidian, accounting, agent, nlp]
author: lovepigpanda
github: https://github.com/lovepigpanda/obsidian-personal-finance-tracker
---

# Obsidian Finance Track — AI Agent 记账技能

> 本 Skill 驱动 AI Agent 完成自然语言记账：解析用户输入 → 匹配分类/账户 → 创建 md 交易文件 → 更新仪表盘

---

## 🚨 强制入口：Onboarding 状态检查（AI Agent 必读）

**加载本 Skill 后第一件事** —— 在做任何记账操作之前：

```python
# 伪代码: 任何 agent 加载本技能后必须执行
vault = os.path.expanduser("~/Obsidian/finance")
config_file = os.path.join(vault, "Accounts/agent-config.md")

if not os.path.exists(config_file):
    # ⚠️ 哨兵文件不存在 = 未初始化
    print("⚠️ 检测到首次使用本技能，必须先完成 Onboarding")
    # 立即跳转「步骤 0: Onboarding」章节 (L194+)
    # 不要执行任何记账/校验/总结操作
else:
    # 已初始化，正常进入记账流程
    pass
```

**为什么这是强制的**：

| 情况 | 后果 |
|------|------|
| 用户没初始化就记账 | 账户列表为空 → 校验失败；定时任务没配 → Agent 不会主动提醒；用户享受不到 #23–#36 的主动功能 |
| 初始化但跳过定时任务 | Agent 只能"被动等用户开会话"，会话外无法主动通知（违反 Agent 是主动管家的定位） |
| **Onboarding 7 步 = 启用本技能的必要条件**，不是可选项 | 任何 agent 跳过 Onboarding = 本次加载视为失败 |

**Onboarding 完成判定**：`Accounts/agent-config.md` 文件存在且包含 `onboarded: true` 字段。

**已完成 Onboarding 的用户如何再次访问配置？** — 直接说 "重新配置" / "重做 Onboarding"，agent 应重新走 7 步（**先备份现有 config**）。

---

## 数据存储架构 ⚠️ 必读

**技能代码与账本数据完全分离**，这是本项目的核心设计原则：

```
GitHub 仓库                          本地 Obsidian vault（私有，不上传）
─────────────────                    ─────────────────────────────
obsidian-personal-finance-tracker    ~/Obsidian/finance/
├── skills/                        ← 技能代码，同步自 GitHub
│   └── obsidian-finance-track/
├── zh/                            ← 模板、规则、文档（可分发）
│   ├── AGENTS.md                  ← AI Agent 工作流
│   ├── Templates/                 ← Templater 模板文件
│   ├── Categories/               ← 分类规则
│   └── Dashboards/               ← Dataview 仪表盘模板
└── README.md                      ← 项目说明

                                    ~/Obsidian/finance/
                                    ├── Templates/             ← 本地副本（用户定制）
                                    ├── Categories/            ← 本地副本（用户定制）
                                    ├── Dashboards/            ← 本地副本（用户定制）
                                    ├── Accounts/              ← 账户列表（含余额）
                                    ├── Transactions/          ← ⭐ 你的真实账本数据
                                    │   ├── expenses/          ← 每笔支出一个 md 文件
                                    │   ├── incomes/           ← 每笔收入一个 md 文件
                                    │   └── transfers/         ← 每笔转账 2 个文件（out+in 配对）
                                    │       ├── out/           ← 转出文件
                                    │       └── in/            ← 转入文件
                                    └── SKILL.md              ← 本地技能副本
```

### 为什么这样设计？

| 对比项 | GitHub 项目（技能） | 本地 vault（数据） |
|--------|-------------------|-------------------|
| 内容 | 模板、规则、脚本、说明文档 | 你的真实交易记录 |
| 同步 | `git pull` 从 GitHub 更新 | 永远不上传，私有 |
| 定制 | 可以提交 PR 优化通用规则 | 用户自己的账户、备注 |
| 风险 | 误操作不会影响账本数据 | 账本数据完全隔离 |

### 更新流程

```bash
# 1. 更新技能代码（从 GitHub 拉取最新模板/规则）
git -C ~/Project/obsidian-personal-finance-tracker pull

# 2. 如需将新模板同步到本地 vault，手动复制
cp ~/Project/obsidian-personal-finance-tracker/zh/Templates/* ~/Obsidian/finance/Templates/

# 3. 账本数据（~/Obsidian/finance/Transactions/）无需任何操作，完全自主
```

---

## 本地 vault 路径

```
~/Obsidian/finance/
```

**目录结构：**

```
~/Obsidian/finance/
├── Templates/                     ← Templater 模板（Templater 插件自动调用）
│   ├── expense-template.md        ← 支出记录模板
│   └── income-template.md         ← 收入记录模板
├── Categories/                    ← 分类规则（AI Agent 读取）
│   ├── expense-categories.md      ← 支出分类说明
│   ├── expense-category-rules.md  ← 支出关键词映射
│   ├── income-categories.md       ← 收入分类说明
│   └── income-category-rules.md  ← 收入关键词映射
├── Dashboards/                    ← Dataview 仪表盘
│   └── finance-dashboard.md       ← 主仪表盘
├── Accounts/                      ← 账户列表
│   └── account-list.md            ← 账户名称+初始余额
├── Transactions/                  ← ⭐ 真实账本数据（本地私有）
    ├── expenses/                  ← 每笔支出一个 .md 文件
    │   └── YYYY-MM-DD-*-ACTIVE.md
    ├── incomes/                   ← 每笔收入一个 .md 文件
    │   └── YYYY-MM-DD-*-ACTIVE.md
    └── transfers/                 ← 每笔转账 2 个文件（out+in 共用 transfer_pair_id）
        ├── out/                   ← 转出文件
        └── in/                    ← 转入文件
```

---

## 工作原理

```
用户自然语言输入
       ↓
AI Agent 读取 ~/Obsidian/finance/Categories/*.md（分类规则）
       ↓
解析字段：type / date / amount / currency / category / account / note
       ↓
判断 type：
  - expense  → 写入 ~/Obsidian/finance/Transactions/expenses/
  - income   → 写入 ~/Obsidian/finance/Transactions/incomes/
  - transfer → 创建 2 个文件（out + in），共用 transfer_pair_id
       ↓
Dataview 仪表盘（~/Obsidian/finance/Dashboards/finance-dashboard.md）自动更新
```

---

## 触发条件

满足以下任一条件时，加载此 Skill：

1. **明确触发词**：记账、记一笔、花了、买了、支出、收入、收到、工资、消费
2. **财务关键词**：支付宝、微信支付、银行卡、报销、退款、红包、余额
3. **英文关键词**：expense、income、spent、paid、received、salary、budget
4. **意图判断**：用户描述了一笔钱进出（不管用什么词）

---

## 🎯 Agent 定位: 主动管家, 不是被动工具

**这个项目的核心定位**: 用这个项目的人都有 AI Agent, 所以 Agent **不是计算器, 是管家**。

| 被动 ❌ | 主动 ✅ |
|---------|---------|
| 用户说"记一笔"才工作 | 会话开始就主动检查数据健康 |
| 等用户问"这个月花了多少" | 主动说"你餐饮超预算 20%" |
| 用户配 cron / launchd | **Agent 主动问**"要不要我帮你配每日校验?" |
| 用户配 webhook 通知 | **Agent 用自己已有的通道**主动推送 |
| 等用户发现错误 | 提前发现并告警 |

**判断标准**: 如果一件事**用户必须主动做**才能享受, 那就是 Agent 失职。

---

## 🚀 步骤 0: Onboarding (新用户引导)

**触发**: 用户第一次加载本技能 (或说"装好了"/"开始用")。

**不要默默开始记账**。先做 7 步配置（完整内容见 [AGENTS-PROACTIVE.md](../../zh/AGENTS-PROACTIVE.md)）:

1. **确认 vault 目录** — 默认 `~/Obsidian/finance`, 确认或改
2. **验证必需文件** — 检查 Templates / Categories / Dashboards / Accounts 都在, 缺的主动帮 cp
3. **引导填账户列表** — 问"你有哪些账户", 帮写 `Accounts/account-list.md` (信用卡账户问账单日/还款日)
4. **配置定时提醒** — **核心!** 主动问"要不要我帮你配以下定时任务?" (Agent 会**帮用户生成** plist/cron, 用户复制粘贴就行):
   - **每日 18:00** 跑 daily_integrity_check.py (包括 #33 记账频率、#34 账户遗忘检测)
   - **每周日 20:00** 跑 weekly_summary.py (#35 周末复盘)
   - **每月最后一日 21:00** 跑 monthly_summary.py (#36 月末自检)
   - **每日 8:00** 跑 credit_card_reminder.py (信用卡临近账单日/还款日时提醒, #23)
   - **每日 8:05** 跑 installment_check.py (分期 PENDING 到期检查, #24)
   - **每日 8:10** 跑 loan_payment_reminder.py (贷款月供提醒, #37)
5. **配置通知偏好** — 主动问"校验失败时我用我自己的通道 (飞书/微信) 发给你, 还是写 alerts.md?"
6. **保存配置 + 写哨兵** — 写到 `Accounts/agent-config.md` (用户可见、可改), **必须** 包含 `onboarded: true` 字段。模板见下方。
7. **试一笔** — 验证整个流程通

**`Accounts/agent-config.md` 模板** (Agent 主动生成, 用户确认):

```markdown
---
title: Agent Configuration
type: agent-config
onboarded: true
onboarded_at: 2026-06-02
agent_name: Hermes
notification_channel: feishu   # feishu | wechat | alerts-md
vault_path: ~/Obsidian/finance
scheduled_tasks:
  - time: "18:00"
    script: daily_integrity_check.py
    enabled: true
  - time: "20:00"
    script: weekly_summary.py
    weekday: sunday
    enabled: true
  - time: "21:00"
    script: monthly_summary.py
    day: last
    enabled: true
  - time: "08:00"
    script: credit_card_reminder.py
    enabled: true
  - time: "08:05"
    script: installment_check.py
    enabled: true
  - time: "08:10"
    script: loan_payment_reminder.py
    enabled: true
---

# AI Agent 配置

> 本文件由 AI Agent 在 Onboarding 时生成, 用户可手动修改。
> **重要**: `onboarded: true` 是 Onboarding 完成哨兵, 删除它 = 强制重做 Onboarding。
> 修改后请告知 Agent, 让它重新校验配置完整性。
```

**为什么不只靠 `agent-config.md` 存在判断**:
- 用户可能误删文件 → 哨兵丢失 → 强制重做 Onboarding (保护性)
- 用户可能改坏内容 → 缺 `onboarded: true` 字段 → 强制重做
- 只有 "文件存在 + onboarded: true + 5 个 scheduled_tasks 都 enabled" 才算真正完成

**为什么需要定时任务**:
- Agent 只在**用户开会话**时才在线。会话关了, Agent 就"睡"了。
- 想让 Agent 主动提醒用户 ("该还款了"/"今天没记账"), Agent 必须在**指定时间被唤醒**——只有系统定时任务能保证。
- Agent 的责任是**主动帮用户配**定时任务 + **主动分析 alerts.md**, 不是逃避定时任务。

---

## 执行流程（AI Agent 标准步骤）

### 步骤 1：识别意图

用户输入 → 判断是**支出 / 收入 / 转账**三种之一

| 支出关键词 | 收入关键词 | 转账关键词 |
|-----------|-----------|-----------|
| 花、买、付、消费、支出、开支 | 收、到、进、赚、工资、奖金、收入 | 转、转给、打给、调拨、还信用卡、from X to Y |

> **重要**：识别到转账意图时，**必须**走双文件配对流程（见步骤 5-6），不要当作支出或收入。

### 步骤 2：提取字段

从用户输入中提取以下字段：

**支出 / 收入：**

| 字段 | 提取方法 | 示例 |
|------|---------|------|
| `type` | 意图判断 | "花了45元" → expense |
| `date` | 时间词 → YYYY-MM-DD | "今天" → 2026-06-01，"昨天" → 2026-05-31 |
| `amount` | 数字提取 | "45元" → 45 |
| `currency` | 币种关键词 | "元" → CNY，"刀" → USD，"€" → EUR |
| `account` | 支付工具匹配 | "支付宝" → Alipay |
| `category` | 关键词 → 分类 | 见下方分类映射表 |
| `note` | 原始描述 | 用户原话 |
| `status` | 固定值 | ACTIVE |

**转账（额外字段）：**

| 字段 | 提取方法 | 示例 |
|------|---------|------|
| `type` | 转账意图 | "从支付宝转 5000 到招行" → transfer |
| `from_account` | 来源账户 | "支付宝" → Alipay |
| `to_account` | 目标账户 | "招行" → CMB |
| `transfer_pair_id` | 自动生成 | `T-2026-06-01-abc123`（out 和 in 共用） |
| `amount` | 数字 | 5000 |
| `currency` | 币种 | CNY |
| `category` | 固定值 | Transfer |

### 步骤 3：匹配分类

读取 `~/Obsidian/finance/Categories/expense-category-rules.md` 或 `income-category-rules.md` 中的分类映射表：

**支出分类（12类）**

| 分类 | 中文关键词 | 英文关键词 |
|------|----------|-----------|
| Food | 午餐、晚餐、外卖、餐厅、沙县 | lunch、dinner、takeout、restaurant |
| Transport | 地铁、公交、打车、滴滴 | subway、bus、taxi、DiDi |
| Shopping | 淘宝、京东、拼多多、超市 | Taobao、JD、Pinduoduo、shopping |
| Entertainment | 电影、游戏、会员、Steam | movie、game、Netflix、Steam |
| Health | 医院、药店、体检 | hospital、pharmacy、checkup |
| Education | 课程、书籍、培训 | course、book、training |
| Housing | 房租、物业、水电 | rent、property、utilities |
| Communication | 话费、宽带、流量 | phone、broadband、data |
| Gift | 红包、礼物、人情 | red envelope、gift、treat |
| Travel | 机票、酒店、旅游 | flight、hotel、travel |
| Investment | 理财、基金、股票 |理财、fund、stock |
| Other | 其他、杂项 | other、misc |

**收入分类（7类）**

| 分类 | 中文关键词 | 英文关键词 |
|------|----------|-----------|
| Salary | 工资、月薪、底薪 | salary、wages |
| Bonus | 年终奖、奖金、绩效 | bonus、year-end |
| Freelance | 兼职、外快、接单 | freelance、side job |
| Investment | 理财利息、投资收益 | investment interest |
| Refund | 退款、退货、补偿 | refund、compensation |
| Gift | 红包、礼金 | red envelope、gift money |
| Other | 其他、偶然收入 | other |

### 步骤 4：匹配账户

根据支付工具匹配账户名：

| 账户 | 中文关键词 | 英文关键词 |
|------|----------|-----------|
| Alipay | 支付宝 | Alipay |
| WeChat Pay | 微信、微信支付 | WeChat、WeChat Pay |
| CMB | 招行、招商银行 | CMB、China Merchants Bank |
| ICBC | 工行、工商银行 | ICBC |
| Credit Card | 信用卡 | Credit Card |
| Cash | 现金 | Cash |
| USD Account | 美元账户 | USD Account |

### 步骤 5：生成文件名

**支出 / 收入：**
```
{date}-{description}-{amount}-{CURRENCY}-ACTIVE.md
```
示例：`2026-06-01-lunch-45-CNY-ACTIVE.md`

**转账（双文件）：**
```
out: {date}-transfer-out-{from_account}-to-{to_account}-{amount}-{CURRENCY}-ACTIVE.md
in:  {date}-transfer-in-{to_account}-from-{from_account}-{amount}-{CURRENCY}-ACTIVE.md
```
示例：
```
2026-06-01-transfer-out-Alipay-to-CMB-5000-CNY-ACTIVE.md
2026-06-01-transfer-in-CMB-from-Alipay-5000-CNY-ACTIVE.md
```

### 步骤 6：创建文件

**文件路径（本地 vault）：**
- 支出：`~/Obsidian/finance/Transactions/expenses/{filename}`
- 收入：`~/Obsidian/finance/Transactions/incomes/{filename}`
- 转账 out：`~/Obsidian/finance/Transactions/transfers/out/{filename}`
- 转账 in：`~/Obsidian/finance/Transactions/transfers/in/{filename}`

**转账文件 frontmatter：**
```yaml
---
type: transfer
date: 2026-06-01
amount: 5000
currency: CNY
category: Transfer
from_account: Alipay
to_account: CMB
transfer_pair_id: T-2026-06-01-abc123   # ⚠️ out 和 in 必须完全一致
note: "还信用卡前调拨"
tags: [transfer, finance]
status: ACTIVE
created: 2026-06-01
---

**文件内容格式：**
```markdown
---
type: expense
date: 2026-06-01
amount: 45
currency: CNY
category: Food
account: Alipay
payment_method: Alipay
note: "午餐-沙县小吃"
tags: [expense, food]
status: ACTIVE
created: 2026-06-01
---

# 2026-06-01 — Lunch Expense

| 字段 | 值 |
|------|---|
| **类型** | 支出 |
| **日期** | 2026-06-01 |
| **金额** | 45 CNY |
| **分类** | Food 🍔 |
| **账户** | Alipay |
| **备注** | 午餐-沙县小吃 |
```

### 步骤 7：确认完成

告诉用户：
- **支出/收入**：文件路径 + 主要内容
- **转账**：2 个文件路径 + 配对 ID（关键！用户后续用 ID 查询配对）
- 可在 Dataview 仪表盘 `~/Obsidian/finance/Dashboards/finance-dashboard.md` 查看汇总

### 步骤 7.5：自动校验（强烈推荐）

写入交易文件后，AI Agent **必须**调用校验脚本以保证项目内部一致性：

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/validate_transaction.py <新文件路径>
```

**校验内容**：必填字段、金额合法、日期合法、币种合法、账户已注册、转账配对完整且一致。

**退出码**：
- `0` = 通过，安静继续
- `1` = 失败，**软告警**——文件保留，AI Agent 告诉用户问题并询问：(a) 帮你修 / (b) 忽略 / (c) 删除重录
- `2` = 文件找不到，参数错误

**典型错误与对话**：
> ❌ 校验失败: 2026-06-01-lunch-45-CNY-ACTIVE.md
>   ❌ [ERROR] amount 必须 > 0 (当前: 0)
>
> AI Agent: "这笔校验失败（amount 必须是正数）。你想：(a) 我帮你改成 45 重新保存 / (b) 这笔金额确实是 0（罕见，比如退款为 0）忽略此告警 / (c) 删除这笔重新录？"

**为什么必须跑校验**：用户只输入初始余额，所有加减都是项目处理——如果项目内部计算错（转账配对丢失、字段填错），余额就不准了。校验脚本保证**项目自己算的不会错**。

---

## 完整示例

### 示例 1：支出

**用户输入：**
> "今天午餐沙县花了45元，支付宝付款"

**AI Agent 执行：**
1. type = expense
2. date = 今天 → 2026-06-01
3. amount = 45, currency = CNY
4. account = Alipay
5. 关键词"午餐、沙县" → category = Food
6. note = "午餐-沙县小吃"
7. 创建文件：`~/Obsidian/finance/Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

### 示例 2：收入

**用户输入：**
> "收到了6月份工资15000元，是招行发的"

**AI Agent 执行：**
1. type = income
2. date = 今天 → 2026-06-01
3. amount = 15000, currency = CNY
4. account = CMB
5. 关键词"工资" → category = Salary
6. note = "6月工资"
7. 创建文件：`~/Obsidian/finance/Transactions/incomes/2026-06-01-salary-15000-CNY-ACTIVE.md`

### 示例 3：多币种支出

**用户输入：**
> "在亚马逊买了本技术书花了35美元，信用卡支付"

**AI Agent 执行：**
1. type = expense
2. date = 今天
3. amount = 35, currency = USD
4. account = Credit Card
5. 关键词"书" → category = Education
6. note = "技术书-亚马逊"
7. 创建文件：`~/Obsidian/finance/Transactions/expenses/2026-06-01-book-35-USD-ACTIVE.md`

### 示例 4：转账

**用户输入：**
> "从支付宝转 5000 到招行，准备还信用卡"

**AI Agent 执行：**
1. type = **transfer**（识别"转"）
2. date = 今天 → 2026-06-01
3. amount = 5000, currency = CNY
4. from_account = Alipay（"支付宝"）
5. to_account = CMB（"招行"）
6. 生成 pair_id = `T-2026-06-01-abc123`
7. category = Transfer（固定）
8. 创建 2 个文件：
   - `~/Obsidian/finance/Transactions/transfers/out/2026-06-01-transfer-out-Alipay-to-CMB-5000-CNY-ACTIVE.md`
   - `~/Obsidian/finance/Transactions/transfers/in/2026-06-01-transfer-in-CMB-from-Alipay-5000-CNY-ACTIVE.md`

**告知用户：**
> 转账已记录（配对 ID：`T-2026-06-01-abc123`）
> - 转出：Alipay → 5000 CNY → `~/Obsidian/finance/Transactions/transfers/out/2026-06-01-transfer-out-Alipay-to-CMB-5000-CNY-ACTIVE.md`
> - 转入：CMB ← 5000 CNY ← `~/Obsidian/finance/Transactions/transfers/in/2026-06-01-transfer-in-CMB-from-Alipay-5000-CNY-ACTIVE.md`
> 查询配对：在 Obsidian 全局搜索 `transfer_pair_id: T-2026-06-01-abc123` 可同时找到两端

---

## 注意事项

1. **日期格式**：统一 `YYYY-MM-DD`，"今天"自动转为当前日期
2. **金额**：纯数字不含符号（如 `45` 而非 `¥45`）
3. **描述**：英文或拼音，用 `-` 连接（如 `lunch`、`subway`、`salary`）
4. **状态**：新建文件一律 `status: ACTIVE`
5. **多币种**：按用户描述如实记录，不转换
6. **关键词匹配**：精准词优先（如"沙县"→Food），再宽泛词（如"其他"→Other）
7. **默认账户**：用户未指定则默认 Alipay（支出）或 CMB（收入）
8. **文件位置**：统一在 `~/Obsidian/finance/Transactions/`
9. **转账识别**：检测到"转 / 打给 / 调拨 / 还信用卡 / from X to Y"等触发词时，**必须**走双文件配对流程，不要当作支出或收入
10. **配对 ID 一致性**：转账 out 和 in 两个文件的 `transfer_pair_id` **必须完全一致**，否则查询配对会失败
11. **配对 ID 唯一性**：每次转账生成新的 `T-{date}-{random-string}`，避免和历史数据冲突

---

## 本地文件路径速查

| 文件 | 路径 |
|------|------|
| AI Agent 工作流 | `~/Project/obsidian-personal-finance-tracker/zh/AGENTS.md` |
| 分类/账户映射 | `~/Project/obsidian-personal-finance-tracker/zh/QUICK-REFERENCE.md` |
| 支出分类规则 | `~/Obsidian/finance/Categories/expense-category-rules.md` |
| 收入分类规则 | `~/Obsidian/finance/Categories/income-category-rules.md` |
| 转账分类 | `~/Obsidian/finance/Categories/transfer-categories.md` |
| 仪表盘 | `~/Obsidian/finance/Dashboards/finance-dashboard.md` |
| 账户列表 | `~/Obsidian/finance/Accounts/account-list.md` |
| 支出模板 | `~/Obsidian/finance/Templates/expense-template.md` |
| 收入模板 | `~/Obsidian/finance/Templates/income-template.md` |
| 转账模板 | `~/Obsidian/finance/Templates/transfer-template.md` |
| **账本数据** | `~/Obsidian/finance/Transactions/{expenses,incomes,transfers/{out,in}}/` |

---

## 校验脚本（scripts/）— Agent 调用的工具, 不是独立服务

项目自带的 Python 校验脚本, **零依赖**（仅用 Python 3.8+ 标准库）。所有用户、所有平台、所有 AI Agent 都能用。

**核心定位变化**: 脚本本身**不**自动跑、不依赖系统 cron、不发 webhook——**全部由 Agent 主动调用 + 用 Agent 自己的通道通知**。

### scripts/validate_transaction.py — 单笔校验

**何时用**: AI Agent 写完每笔交易文件后**立即**调用（步骤 7.5）。**这是 Agent 的责任, 不是用户的**。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/validate_transaction.py <新文件路径>
```

校验内容: 必填字段、金额 > 0、日期合法、币种合法、账户已注册、**transfer 配对完整且字段一致**。

### scripts/daily_integrity_check.py — 每日守恒

**何时用**: **Agent 自己在会话开始时判断**"该跑了吗", 跑就调, 不依赖系统 cron。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py
```

校验内容:
1. 所有 transfer 的 out 和 in 都成对存在（不孤立）
2. 配对文件的 amount、currency、from_account、to_account 完全一致
3. 每币种的 transfer_in == transfer_out（转账自洽）
4. Python 算余额 vs 累加验证（路径 A vs 路径 B 自洽——这是核心保证）
5. 账户透支检查（软告警）

### scripts/weekly_dashboard_check.py — 周度结构检查

**何时用**: Agent 周日 8 点主动调。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/weekly_dashboard_check.py
```

校验内容: 仪表盘文件引用了所有必要字段、账户表完整、打印权威余额供用户对账 Dataview 显示。

### scripts/credit_card_reminder.py — 信用卡还款提醒 (#23)

**何时用**: Agent 帮用户配每日 8:00 定时任务。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/credit_card_reminder.py --vault ~/Obsidian/finance
```

校验内容:
- 扫 `Accounts/account-list.md` 找 `type: credit` 账户
- 对每张卡算下次出账日 + 还款日 (处理跨月、月末)
- 还款日 ≤ 5 天 → WARN, 已过 → ERROR
- 写到 `alerts.md`

**前置**: 信用卡账户必须在 `account-list.md` 写 `statement_day` + `payment_due_day` 字段, 否则报 INFO 提示补字段 (软告警, 不阻塞)。

### scripts/installment_check.py — 分期完整性检查 (#24)

**何时用**: Agent 帮用户配每日 8:05 定时任务。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/installment_check.py --vault ~/Obsidian/finance
```

校验内容:
- 按 `installment_group_id` 聚合所有分期 expense
- 校验 ① 总期数 ② 字段一致性 (amount/currency/account/category) ③ PENDING 是否到期 ④ 孤立分期 (只有 1 期但标记分期)
- 写到 `alerts.md`

### scripts/loan_payment_reminder.py — 贷款月供提醒 (#37)

**何时用**: Agent 帮用户配每日 8:10 定时任务 (与 credit_card / installment 错开 5 分钟)。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/loan_payment_reminder.py --vault ~/Obsidian/finance
```

**触发条件**: 检测到 `Accounts/account-list.md` 中存在 `type: loan` 的账户。

**校验内容**:
- 贷款账户必填字段检查 (贷款总额 / 月供 / 剩余期数 / 起始月), 缺失报 INFO
- 下次月供日计算: 起始月最后一天, 之后每月同日 (自动处理 2 月天数)
- **≤5 天**: WARN ("月供临近, 金额 X")
- **已过 ≤3 天未记账**: ERROR ("月供已过 X 天未还!")
- **已过 4+ 天未记账**: ERROR ("严重逾期")
- **当月已记账**: INFO ("已还, 下次月供...")

**支持 4 个贷款字段** (zh + en): `贷款总额/Principal` / `月供/Monthly Payment` / `剩余期数/Remaining Months` / `起始月/Start Month`

**配套**: `monthly_summary.py` 月末报告自动添加"💳 贷款账户进度"段 (贷款总额 / 已还 / 百分比 / 剩余期数)

---

### scripts/installment_helper.py — 分期模板生成器 (#24)

**何时用**: 用户写完第一期 expense 后, Agent **立即调**。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/installment_helper.py create \
  --first-file ~/Obsidian/finance/Transactions/expenses/<第一期文件> \
  --total 12
```

做什么:
- 读第一期 frontmatter, 复制 amount/currency/account/category/note
- 自动生成 N-1 个 PENDING expense 模板 (日期递增)
- 缺 `installment_group_id` 时自动生成 `INS-{date}-{account}-{amount}` 格式
- 用户实际扣款时, 改 status=PENDING → ACTIVE, 再调 `validate_transaction.py`

### scripts/weekly_summary.py — 周末复盘 (#35)

**何时用**: Agent 帮用户配每周日 20:00 定时任务。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/weekly_summary.py --vault ~/Obsidian/finance
```

校验内容:
- 范围: 本周一 00:00 ~ 本周日 23:59
- 输出: 笔数 / 总支出 / 总收入 / 分类前 3 / 账户余额变化 / vs 上周同比
- 写到 `alerts.md`

**Agent 后续**: 读 `alerts.md`, 把"本周 23 笔, 餐饮 ¥820 (降 32%)"用自己通道推给用户。

### scripts/monthly_summary.py — 月末自检 (#36)

**何时用**: Agent 帮用户配每月最后一日 21:00 定时任务。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/monthly_summary.py --vault ~/Obsidian/finance
# 历史月份
python3 ~/Project/obsidian-personal-finance-tracker/scripts/monthly_summary.py --vault ~/Obsidian/finance --month 2026-03
```

校验内容:
- 范围: 当月 1 号 ~ 当月最后一天 (未结束则截止到今日)
- 输出: 笔数 / 支出 / 收入 / 储蓄率 / 分类汇总 / 跨账户流量
- 写到 `alerts.md`

**储蓄率公式**: `(收入 - 支出) / 收入` (转出不算支出, transfer_in/out 算跨账户流量)。

### 通知方式 (脚本只做最基础的, Agent 做剩下的)

脚本**只**做两件事 (不依赖任何配置):

1. **`~/Obsidian/finance/Dashboards/alerts.md`** — 始终写入, 用户在 Obsidian 里看
2. **桌面通知** — macOS `osascript` / Linux `notify-send`, 弹窗提醒

**其他通知 (飞书 / 微信 / 邮件 / 短信) 全部由 Agent 负责**——Agent 读 alerts.md 后, 用自己已有的消息通道主动推给用户。**不要**让用户去配 webhook / 申请 Bark key / 注册 Server 酱——那是 Agent 的事, 不是用户的。

详细主动行为规则见 [AGENTS-PROACTIVE.md](../../zh/AGENTS-PROACTIVE.md)。

---

## 首次安装说明

如果你是从 GitHub 首次安装，请按以下步骤操作：

```bash
# 1. 克隆项目到本地
git clone https://github.com/lovepigpanda/obsidian-personal-finance-tracker.git ~/Project/obsidian-personal-finance-tracker

# 2. 在 Obsidian vault 中创建 finance 目录
mkdir -p ~/Obsidian/finance/{Templates,Categories,Dashboards,Accounts,Transactions/{expenses,incomes,transfers/{out,in}}}

# 3. 复制模板和规则文件到 vault
cp ~/Project/obsidian-personal-finance-tracker/zh/Templates/*.md ~/Obsidian/finance/Templates/
cp ~/Project/obsidian-personal-finance-tracker/zh/Categories/*.md ~/Obsidian/finance/Categories/
cp ~/Project/obsidian-personal-finance-tracker/zh/Dashboards/*.md ~/Obsidian/finance/Dashboards/
cp ~/Project/obsidian-personal-finance-tracker/zh/Accounts/*.md ~/Obsidian/finance/Accounts/

# 4. 安装技能到各 AI Agent
aweskill install https://github.com/lovepigpanda/obsidian-personal-finance-tracker
aweskill agent add --agent openclaw skill obsidian-finance-track
aweskill agent add --agent claude-code skill obsidian-finance-track
```

> 注意：`Transactions/` 目录不要从 GitHub 复制——它是你的私人账本。

---

> Skill: obsidian-finance-track | Version: V1.0 | For AI Agent use
> Project: https://github.com/lovepigpanda/obsidian-personal-finance-tracker