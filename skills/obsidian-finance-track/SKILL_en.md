---
name: obsidian-finance-track
description: >
  Obsidian Personal Finance Tracking AI Agent Skill. Loads when user describes anything finance-related
  (expense, income, transfer, wallet balance, salary, spending, etc.) or uses trigger words like
  "记账" (record expense), "记一笔" (log one), "花了" (spent), "买了" (bought), "收到" (received), etc.

  Supports Chinese and English users, auto-parses natural language input, creates transaction .md files
  in Obsidian vault, and updates Dataview dashboard.

  Project files: ~/Project/obsidian-personal-finance-tracker/zh/ (Chinese primary) or en/ (English)
  AI Agent workflow: zh/AGENTS.md | Category mapping: zh/QUICK-REFERENCE.md
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
  - lunch
  - dinner
  - Alipay
  - WeChat Pay
  - bank card
  - reimbursement
  - refund
  - red envelope
  - balance
  - account
  - salary
  - bonus
version: V1.0
status: ACTIVE
tags: [finance, obsidian, accounting, agent, nlp]
author: lovepigpanda
github: https://github.com/lovepigpanda/obsidian-personal-finance-tracker
---

# Obsidian Finance Track — AI Agent Accounting Skill

> This skill enables AI Agent to handle natural language accounting: parse user input → match category/account → create md transaction file → update dashboard

---

## How It Works

```
User natural language input
       ↓
AI Agent reads AGENTS.md + QUICK-REFERENCE.md
       ↓
Parse fields: type / date / amount / currency / category / account / note
       ↓
Write to Obsidian vault (~/Project/obsidian-personal-finance-tracker/zh/)
       ↓
Dataview dashboard auto-updates
```

---

## Trigger Conditions

Load this skill when ANY of the following is true:

1. **Explicit triggers**: 记账 (record), 记一笔 (log one), 花 (spent), 买 (bought), 支出 (expense), 收入 (income), 收到 (received), 工资 (salary), 消费 (spending)
2. **Finance keywords**: 支付宝 (Alipay), 微信支付 (WeChat Pay), 银行卡 (bank card), 报销 (reimbursement), 退款 (refund), 红包 (red envelope), 余额 (balance)
3. **English triggers**: expense, income, spent, paid, received, salary, budget, freelance
4. **Intent detection**: User describes money in/out (regardless of wording)

---

## Execution Flow (AI Agent Standard Steps)

### Step 1: Identify Intent

User input → determine **expense** or **income**

| Expense keywords | Income keywords |
|------------------|-----------------|
| 花、买、付、消费、支出、开支 | 收、到、进、赚、工资、奖金、收入 |
| spent、bought、paid、expense | received、got paid、salary、income |

### Step 2: Extract Fields

Extract from user input:

| Field | Method | Example |
|-------|--------|---------|
| `type` | Intent detection | "spent 45 CNY" → expense |
| `date` | Time words → YYYY-MM-DD | "today" → 2026-06-01 |
| `amount` | Number extraction | "45 CNY" → 45 |
| `currency` | Currency keyword | "CNY" → CNY, "$" → USD |
| `account` | Payment tool matching | "Alipay" → Alipay |
| `category` | Keyword → category | See mapping below |
| `note` | Raw description | User's original text |
| `status` | Fixed value | ACTIVE |

### Step 3: Match Category

Read category mapping from `QUICK-REFERENCE.md`:

**Expense Categories (12)**

| Category | Chinese Keywords | English Keywords |
|----------|-----------------|-------------------|
| Food | 午餐、晚餐、外卖、餐厅、沙县 | lunch、dinner、breakfast、takeout、restaurant |
| Transport | 地铁、公交、打车、滴滴 | subway、bus、taxi、DiDi、parking |
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

**Income Categories (7)**

| Category | Chinese Keywords | English Keywords |
|----------|-----------------|-------------------|
| Salary | 工资、月薪、底薪 | salary、wages、base pay |
| Bonus | 年终奖、奖金、绩效 | bonus、year-end bonus |
| Freelance | 兼职、外快、接单 | freelance、side job、gig |
| Investment | 理财利息、投资收益 | investment interest |
| Refund | 退款、退货、补偿 | refund、compensation |
| Gift | 红包、礼金 | red envelope、gift money |
| Other | 其他、偶然收入 | other |

### Step 4: Match Account

Match payment tool to account name:

| Account | Chinese Keywords | English Keywords |
|---------|-----------------|------------------|
| Alipay | 支付宝 | Alipay |
| WeChat Pay | 微信、微信支付 | WeChat、WeChat Pay |
| CMB | 招行、招商银行 | CMB、China Merchants Bank |
| ICBC | 工行、工商银行 | ICBC |
| Credit Card | 信用卡 | Credit Card |
| Cash | 现金 | Cash |
| USD Account | 美元账户 | USD Account |

### Step 5: Generate Filename

```
{date}-{description}-{amount}-{CURRENCY}-ACTIVE.md
```

Example: `2026-06-01-lunch-45-CNY-ACTIVE.md`

### Step 6: Create File

**File path:**
- Expense: `~/Project/obsidian-personal-finance-tracker/zh/Transactions/expenses/{filename}`
- Income: `~/Project/obsidian-personal-finance-tracker/zh/Transactions/incomes/{filename}`

**File content format:**
```markdown
---
type: expense
date: 2026-06-01
amount: 45
currency: CNY
category: Food
account: Alipay
payment_method: Alipay
note: "Lunch at Shaxian"
tags: [expense, food]
status: ACTIVE
created: 2026-06-01
---

# 2026-06-01 — Lunch Expense

| Field | Value |
|-------|-------|
| **Type** | Expense |
| **Date** | 2026-06-01 |
| **Amount** | 45 CNY |
| **Category** | Food 🍔 |
| **Account** | Alipay |
| **Note** | Lunch at Shaxian |
```

### Step 7: Confirm Completion

Tell user:
- File path
- Main content (type, amount, category, account)
- Can view summary in Dataview dashboard

---

## Complete Examples

### Example 1: Expense

**User input:**
> "Lunch at Shaxian spent 45 CNY, paid via Alipay"

**AI Agent execution:**
1. type = expense
2. date = today → 2026-06-01
3. amount = 45, currency = CNY
4. account = Alipay
5. keywords "lunch, Shaxian" → category = Food
6. note = "Lunch at Shaxian"
7. Create: `Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

### Example 2: Income

**User input:**
> "Received June salary of 15000 CNY, deposited to CMB"

**AI Agent execution:**
1. type = income
2. date = today → 2026-06-01
3. amount = 15000, currency = CNY
4. account = CMB
5. keywords "salary" → category = Salary
6. note = "June salary"
7. Create: `Transactions/incomes/2026-06-01-salary-15000-CNY-ACTIVE.md`

### Example 3: Multi-currency Expense

**User input:**
> "Bought a tech book on Amazon for 35 USD, paid with credit card"

**AI Agent execution:**
1. type = expense
2. date = today
3. amount = 35, currency = USD
4. account = Credit Card
5. keywords "book" → category = Education
6. note = "Tech book - Amazon"
7. Create: `Transactions/expenses/2026-06-01-book-35-USD-ACTIVE.md`

---

## Notes

1. **Date format**: Always `YYYY-MM-DD`, "today" auto-converts to current date
2. **Amount**: Pure number without symbol (e.g. `45` not `¥45`)
3. **Description**: English or Pinyin, connected with `-` (e.g. `lunch`, `subway`, `salary`)
4. **Status**: New files always `status: ACTIVE`
5. **Multi-currency**: Record as stated by user, do not convert
6. **Keyword matching**: Precise keywords first (e.g. "Shaxian" → Food), then broad (e.g. "other" → Other)
7. **Default account**: If user doesn't specify → Alipay (expense) or CMB (income)
8. **File location**: `~/Project/obsidian-personal-finance-tracker/zh/` (Chinese) or `en/` (English)

---

## Project File Paths

| File | Path |
|------|------|
| AI Agent workflow | `~/Project/obsidian-personal-finance-tracker/zh/AGENTS.md` |
| Category/account mapping | `~/Project/obsidian-personal-finance-tracker/zh/QUICK-REFERENCE.md` |
| Expense category rules | `~/Project/obsidian-personal-finance-tracker/zh/Categories/expense-category-rules.md` |
| Income category rules | `~/Project/obsidian-personal-finance-tracker/zh/Categories/income-category-rules.md` |
| Dashboard | `~/Project/obsidian-personal-finance-tracker/zh/Dashboards/finance-dashboard.md` |
| Account list | `~/Project/obsidian-personal-finance-tracker/zh/Accounts/account-list.md` |
| Expense template | `~/Project/obsidian-personal-finance-tracker/zh/Templates/expense-template.md` |
| Income template | `~/Project/obsidian-personal-finance-tracker/zh/Templates/income-template.md` |

---

## Related Files

- [[Finance Dashboard]] — View all transaction summaries
- [[Account List]] — Account balance queries
- [[Expense Categories]] — Full expense category descriptions
- [[Income Categories]] — Full income category descriptions
- [[expense-category-rules.md]] — Category keyword mapping table
- [[income-category-rules.md]] — Income category keyword mapping table

---

> Skill: obsidian-finance-track | Version: V1.0 | For AI Agent use
> Project: https://github.com/lovepigpanda/obsidian-personal-finance-tracker