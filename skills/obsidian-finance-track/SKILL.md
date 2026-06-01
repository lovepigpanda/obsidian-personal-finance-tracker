---
name: obsidian-finance-track
description: >
  Obsidian 个人财务追踪 AI Agent Skill。当用户描述记账相关的内容（支出、收入、转账、钱包余额、工资、消费等）时，
  或明确说"记账"、"记一笔"、"花了多少"、"收到"等触发词时，加载此 Skill。

  支持中文和英文用户，自动解析自然语言输入，在 Obsidian vault 中创建交易 md 文件，并更新 Dataview 仪表盘。

  项目文件位于：~/Project/obsidian-personal-finance-tracker/zh/（中文主要版）或 en/（英文版）
  AI Agent 工作流：zh/AGENTS.md | 分类映射：zh/QUICK-REFERENCE.md
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
  - expense
  - income
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

## 工作原理

```
用户自然语言输入
       ↓
AI Agent 读取 AGENTS.md + QUICK-REFERENCE.md
       ↓
解析字段：type / date / amount / currency / category / account / note
       ↓
写入 Obsidian vault（~/Project/obsidian-personal-finance-tracker/zh/）
       ↓
Dataview 仪表盘自动更新
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

用户输入 → 判断是**支出**还是**收入**

| 支出关键词 | 收入关键词 |
|-----------|-----------|
| 花、买、付、消费、支出、开支 | 收、到、进、赚、工资、奖金、收入 |

### 步骤 2：提取字段

从用户输入中提取以下字段：

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

### 步骤 3：匹配分类

读取 `QUICK-REFERENCE.md` 中的分类映射表，根据 note 关键词匹配：

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

```
{date}-{description}-{amount}-{CURRENCY}-ACTIVE.md
```

示例：`2026-06-01-lunch-45-CNY-ACTIVE.md`

### 步骤 6：创建文件

**文件路径：**
- 支出：`~/Project/obsidian-personal-finance-tracker/zh/Transactions/expenses/{filename}`
- 收入：`~/Project/obsidian-personal-finance-tracker/zh/Transactions/incomes/{filename}`

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
- 文件路径
- 主要内容（type、amount、category、account）
- 可在 Dataview 仪表盘查看汇总

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
7. 创建文件：`Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

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
7. 创建文件：`Transactions/incomes/2026-06-01-salary-15000-CNY-ACTIVE.md`

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
7. 创建文件：`Transactions/expenses/2026-06-01-book-35-USD-ACTIVE.md`

---

## 注意事项

1. **日期格式**：统一 `YYYY-MM-DD`，"今天"自动转为当前日期
2. **金额**：纯数字不含符号（如 `45` 而非 `¥45`）
3. **描述**：英文或拼音，用 `-` 连接（如 `lunch`、`subway`、`salary`）
4. **状态**：新建文件一律 `status: ACTIVE`
5. **多币种**：按用户描述如实记录，不转换
6. **关键词匹配**：精准词优先（如"沙县"→Food），再宽泛词（如"其他"→Other）
7. **默认账户**：用户未指定则默认 Alipay（支出）或 CMB（收入）
8. **文件位置**：`~/Project/obsidian-personal-finance-tracker/zh/`（中文用户）或 `en/`（英文用户）

---

## 项目文件路径

| 文件 | 路径 |
|------|------|
| AI Agent 工作流 | `~/Project/obsidian-personal-finance-tracker/zh/AGENTS.md` |
| 分类/账户映射 | `~/Project/obsidian-personal-finance-tracker/zh/QUICK-REFERENCE.md` |
| 支出分类规则 | `~/Project/obsidian-personal-finance-tracker/zh/Categories/expense-category-rules.md` |
| 收入分类规则 | `~/Project/obsidian-personal-finance-tracker/zh/Categories/income-category-rules.md` |
| 仪表盘 | `~/Project/obsidian-personal-finance-tracker/zh/Dashboards/finance-dashboard.md` |
| 账户列表 | `~/Project/obsidian-personal-finance-tracker/zh/Accounts/account-list.md` |
| 支出模板 | `~/Project/obsidian-personal-finance-tracker/zh/Templates/expense-template.md` |
| 收入模板 | `~/Project/obsidian-personal-finance-tracker/zh/Templates/income-template.md` |

---

## 相关文件

- [[Finance Dashboard]] — 仪表盘查看所有交易汇总
- [[Account List]] — 账户余额查询
- [[Expense Categories]] — 支出分类完整说明
- [[Income Categories]] — 收入分类完整说明
- [[expense-category-rules.md]] — 分类关键词映射表
- [[income-category-rules.md]] — 收入分类关键词映射表

---

> Skill: obsidian-finance-track | Version: V1.0 | For AI Agent use
> Project: https://github.com/lovepigpanda/obsidian-personal-finance-tracker