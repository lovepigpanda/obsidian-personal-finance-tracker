---
name: obsidian-finance-track
tagline: 你的 AI 理财搭档 · Your AI Finance Partner
description: >
  Obsidian 个人财务追踪 AI Agent Skill。当用户描述记账相关的内容（支出、收入、转账、钱包余额、工资、消费等）时，
  或明确说"记账"、"记一笔"、"花了多少"、"收到"、"转给 X"等触发词时，加载此 Skill。

  支持中文和英文用户，自动解析自然语言输入，在 Obsidian vault 中创建交易 md 文件，并更新 Dataview 仪表盘。

  ⚠️ 技能代码与账本数据分离：技能来自 GitHub 同步，账本数据存本地 ~/Obsidian/finance/
  详见「数据存储架构」章节。
triggers:
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
version: V1.0
status: ACTIVE
tags: [finance, obsidian, accounting, agent, nlp]
author: lovepigpanda
github: https://github.com/lovepigpanda/obsidian-personal-finance-tracker
---

# Obsidian Finance Track — AI Agent 记账技能

> 本 Skill 驱动 AI Agent 完成自然语言记账：解析用户输入 → 匹配分类/账户 → 创建 md 交易文件 → 更新仪表盘

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

## 校验脚本（scripts/）

项目自带的 Python 校验脚本，**零依赖**（仅用 Python 3.8+ 标准库）。所有用户、所有平台、所有 AI Agent 都能用。

### scripts/validate_transaction.py — 单笔校验

**何时用**：AI Agent 写完每笔交易文件后立即调用（步骤 7.5）。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/validate_transaction.py <新文件路径>
```

校验内容：必填字段、金额 > 0、日期合法、币种合法、账户已注册、**transfer 配对完整且字段一致**。

### scripts/daily_integrity_check.py — 每日守恒

**何时用**：每天定时跑（cron / launchd / GitHub Actions），不依赖 AI Agent。

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py
```

校验内容：
1. 所有 transfer 的 out 和 in 都成对存在（不孤立）
2. 配对文件的 amount、currency、from_account、to_account 完全一致
3. 每币种的 transfer_in == transfer_out（转账自洽）
4. Python 算余额 vs 累加验证（路径 A vs 路径 B 自洽——这是核心保证）
5. 账户透支检查（软告警）

异常时**自动**写入 `~/Obsidian/finance/Dashboards/alerts.md`、发桌面通知、可选 webhook 推送。

### scripts/weekly_dashboard_check.py — 周度结构检查

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/weekly_dashboard_check.py
```

校验内容：仪表盘文件引用了所有必要字段、账户表完整、打印权威余额供用户对账 Dataview 显示。

### cron 配置（推荐所有人配置）

**macOS launchd** (用户级)：
```bash
# 写 ~/Library/LaunchAgents/com.local.obsidian-finance-daily.plist
# WatchPaths 监控 ~/Obsidian/finance/Transactions/ 新文件
# 程序触发 validate_transaction.py
```

**Linux/macOS crontab**：
```cron
# 每天早 6 点跑守恒
0 6 * * * /usr/bin/python3 ~/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py
```

**GitHub Actions**（适合把 vault 同步到 GitHub 的用户）：见 `.github/workflows/finance-check.yml`（本项目自带）

> **关键设计**：单笔校验由 AI Agent 主动调用（覆盖 80% 场景），系统 cron 兜底（覆盖 100%——包括用户手动用 Templater 录的场景）。

### 通知方式（自动启用）

所有校验异常自动通过以下渠道通知（无需配置）：

1. **`~/Obsidian/finance/Dashboards/alerts.md`** — 始终写入，用户在 Obsidian 里看
2. **桌面通知** — macOS `osascript` / Linux `notify-send`，弹窗提醒
3. **Webhook 推送（可选）** — 配环境变量启用：
   - `BARK_KEY` → Bark（iOS）
   - `PUSHPLUS_TOKEN` → PushPlus（微信）
   - `SCT_KEY` → Server酱（微信）
   - `OBSIDIAN_FINANCE_WEBHOOK_URL` → 通用 webhook

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