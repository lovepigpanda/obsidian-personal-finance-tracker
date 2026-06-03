---
title: AI Agent — Natural Language Finance Tracking Guide
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: agent-guide
tags: [agent, finance, nlp, guide]
description: AI Agent finance system guide — how to parse natural language input and automatically create transaction records
---

# AI Agent Finance Tracking System Guide

> This system is designed for AI Agents (Claude / Hermes / etc.). The AI parses the user's natural language input and automatically creates income / expense records.

---

## System Architecture

```
User natural language input
         ↓
AI Agent parses intent + extracts fields
         ↓
Auto-match categories (reads category-rules)
         ↓
Create .md file (frontmatter + content)
         ↓
Dataview dashboard auto-updates
```

---

## Workflow

### Step 1: Parse User Input

The user describes a transaction in natural language. AI Agent must extract these fields:

| Field | Source | Example |
|-------|--------|---------|
| `type` | Intent detection | "spent" → expense, "received" → income |
| `date` | Time words | "today" → 2026-06-01, "yesterday" → 2026-05-31 |
| `amount` | Number extraction | "45 CNY" → 45, "15000" → 15000 |
| `currency` | Currency | "CNY" → CNY, "$" → USD |
| `category` | Keyword matching | See category mapping table below |
| `account` | Payment tool | "Alipay" → Alipay, "WeChat" → WeChat Pay |
| `payment_method` | Payment method | Same as account field |
| `note` | Raw description | User's original text |
| `status` | Fixed value | `ACTIVE` |

### Step 2: Read Category Mapping Rules

AI Agent reads these files for keyword → category mapping:

- `Categories/expense-category-rules.md` — Expense categories (12 types)
- `Categories/income-category-rules.md` — Income categories (7 types)

### Step 3: Create Transaction File

**File path format:**
```
Transactions/expenses/{YYYY-MM-DD}-{description}-{amount}-{CURRENCY}-{STATUS}.md
Transactions/incomes/{YYYY-MM-DD}-{description}-{amount}-{CURRENCY}-{STATUS}.md
```

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
| **Date** | = this.date |
| **Amount** | = this.amount |
```

---

## Category Mapping Table (Quick Reference)

### Expense Categories

| Category | Example Keywords |
|----------|-----------------|
| Food 🍔 | lunch, dinner, breakfast, takeout, restaurant, food, snack, fast food, Shaxian, hotpot, BBQ, breakfast, midnight snack |
| Transport 🚌 | subway, bus, taxi, uber, parking, gas, train, travel, DiDi, hitchhike, cycling |
| Shopping 🛍️ | Taobao, JD, Pinduoduo, shopping, clothes, shoes, supermarket, daily goods, department store, electronics, phone |
| Entertainment 🎮 | movie, game, music, video, iQIYI, Tencent Video, Steam, Netflix, subscription, KTV |
| Health 💊 | hospital, pharmacy, medicine, checkup, dental, TCM, clinic, medical, see doctor, registration |
| Education 📚 | course, tuition, book, training, exam, subscription, edu, learning, tutorial, extracurricular |
| Housing 🏠 | rent, property, utilities, gas, repair, furniture, renovation, cleaning, housekeeping |
| Communication 📱 | phone, mobile plan, broadband, data, communication, landline |
| Gift 🎁 | red envelope, gift, treat,人情, gift giving, 份子钱 |
| Travel ✈️ | flight, hotel, travel, ticket, vacation, sightseeing, scenic spot |
| Investment 💹 |理财, fund, stock, investment, loss |
| Other ❓ | other, miscellaneous |

### Income Categories

| Category | Example Keywords |
|----------|-----------------|
| Salary 💰 | salary, monthly pay, wages, base salary |
| Bonus 🎉 | year-end bonus, bonus, performance, dividend |
| Freelance 💻 | freelance, side job, gig, contract work,自由职业 |
| Investment 📈 | investment interest, fund dividend, stock gain, dividend |
| Refund 🔄 | refund, return, compensation, 赔偿 |
| Gift 🎁 | red envelope, gift money |
| Other ❓ | other, incidental income |

---

## Account Mapping Table (Quick Reference)

| Account | Keywords | Note |
|---------|----------|------|
| Alipay | Alipay | Alipay |
| WeChat Pay | WeChat, WeChat Pay | WeChat Pay |
| CMB | CMB, China Merchants Bank | China Merchants Bank |
| ICBC | ICBC, Industrial and Commercial Bank | Industrial and Commercial Bank |
| Credit Card | Credit Card | Credit Card |
| Cash | Cash | Cash |
| USD Account | USD Account | USD Account |

### Transfer Trigger Keywords

| Trigger | Intent |
|---------|--------|
| transfer / transfer to / transfer from | transfer |
| transfer out / transfer in | transfer (direction) |
| allocate / rebalance / top up / withdraw | transfer |
| pay credit card / repay card | transfer (out → credit card) |
| from X to Y / X to Y | transfer |

### Default Account Resolution (V1.3.3+ #38)

If the user **didn't specify an account** in the natural language (e.g. "had lunch at Shaxian for 45 CNY"), the Agent should call `scripts/transaction_create.py`, which auto-selects by priority:

1. **User explicit** ("use CMB") → use directly
2. **note implicit** ("bought with Alipay...") → extract from note
3. **config/default_accounts.yaml rules** ("subway|bus" → 交通卡, "repay" → CMB savings, "Food/Shopping/..." → credit card)
4. **learning.json history** ("Shaxian" → previously used account)
5. **fallback** (expense=Alipay, income=CMB, transfer=ask must be explicit)

**Learning mechanism** (ask_on_2nd):
- 1st time using default → silently record to `~/.obsidian-finance/learning.json`
- 2nd time same keyword but different account → Agent must use `clarify` tool to ask "change default?"
- User confirms → update learning

---

## Usage Examples

### Example 1: Expense Recording

**User input:**
> "Lunch at Shaxian spent 45 CNY, paid via Alipay"

**AI Agent processing:**
1. type = expense
2. date = today → 2026-06-01
3. amount = 45, currency = CNY
4. account = Alipay, payment_method = Alipay
5. keywords "lunch, Shaxian" → category = Food
6. note = "Lunch at Shaxian"

**Created file:**
```
Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md
```

---

### Example 2: Income Recording

**User input:**
> "Received June salary of 15000 CNY, deposited to CMB"

**AI Agent processing:**
1. type = income
2. date = today → 2026-06-01
3. amount = 15000, currency = CNY
4. account = CMB, payment_method = Bank Transfer
5. keywords "salary, wages" → category = Salary
6. note = "June salary"

**Created file:**
```
Transactions/incomes/2026-06-01-salary-15000-CNY-ACTIVE.md
```

---

### Example 3: Multi-currency

**User input:**
> "Bought a tech book on Amazon for 35 USD, paid with credit card"

**AI Agent processing:**
1. type = expense
2. date = today → 2026-06-01
3. amount = 35, currency = USD
4. account = Credit Card
5. keywords "book, books" → category = Education
6. payment_method = Credit Card
7. note = "Tech book - Amazon"

**Created file:**
```
Transactions/expenses/2026-06-01-book-35-USD-ACTIVE.md
```

---

### Example 4: Multi-currency Income

**User input:**
> "Received 500 USD for freelancing, via PayPal"

**AI Agent processing:**
1. type = income
2. date = today
3. amount = 500, currency = USD
4. account = PayPal
5. payment_method = PayPal
6. keywords "freelancing, side job" → category = Freelance
7. note = "Freelancing payment"

**Created file:**
```
Transactions/incomes/2026-06-01-freelancing-500-USD-ACTIVE.md
```

---

### Example 5: Transfer

**User input:**
> "Transferred 5000 from Alipay to CMB to pay off credit card"

**AI Agent processing:**
1. Detect type = **transfer** (matched "transfer" + "pay credit card")
2. Parse direction: from = Alipay, to = CMB
3. amount = 5000, currency = CNY
4. category = Transfer (transfer-only category)
5. Generate pair ID = `T-2026-06-01-xxx`
6. **Create 2 files** (out + in, sharing the same `transfer_pair_id`)

**Created files:**
```
Transactions/transfers/out/2026-06-01-transfer-out-Alipay-to-CMB-5000-CNY-ACTIVE.md
Transactions/transfers/in/2026-06-01-transfer-in-CMB-from-Alipay-5000-CNY-ACTIVE.md
```

**Key fields:**
```yaml
type: transfer
amount: 5000
currency: CNY
category: Transfer
from_account: Alipay
to_account: CMB
transfer_pair_id: T-2026-06-01-abc123
```

**Querying the pair:** In Obsidian, global-search `transfer_pair_id: T-2026-06-01-abc123` to locate both the out and in files at once.

---

## AI Agent Operation Checklist

When the user asks to record a transaction, AI Agent should:

### General Workflow

- [ ] **1. Identify intent**: Is it expense / income / transfer?
- [ ] **2. Extract date**: Convert "today / yesterday / the day before yesterday" to standard date format
- [ ] **3. Extract amount**: Number + currency (default CNY)
- [ ] **4. Extract account**: Payment tool → account name (see account mapping table)
- [ ] **5. Match category**: Match category based on note keywords (see category mapping table)
- [ ] **6. Generate filename**: `YYYY-MM-DD-{description}-{amount}-{CURRENCY}-ACTIVE.md`
- [ ] **7. Create file**: Write to the appropriate directory
- [ ] **8. Write frontmatter**: Complete fields
- [ ] **9. Write body**: Standard format table
- [ ] **10. Confirm completion**: Tell user the file path and main content

### Transfer-specific Workflow

- [ ] **T1. Detect transfer intent**: Match trigger words like "transfer / send / allocate / pay credit card / from X to Y"
- [ ] **T2. Parse from/to accounts**: Recognize "X transfer Y" or "from X to Y" patterns
- [ ] **T3. Generate pair ID**: `T-{YYYY-MM-DD}-{random-string}`, shared between out and in
- [ ] **T4. Create 2 files**: One in `Transactions/transfers/out/` and one in `Transactions/transfers/in/`
- [ ] **T5. Write pair field**: `transfer_pair_id` must be **identical** in both files
- [ ] **T6. Tell user the pair ID**: So they can query the counterpart later

---

## Notes

1. **Date format**: Use `YYYY-MM-DD` consistently, e.g. `2026-06-01`
2. **Amount**: Pure number, no currency symbol (e.g. `45` not `¥45`)
3. **Description**: English or Pinyin, connected with `-` (e.g. `lunch`, `subway`, `salary`)
4. **File status**: New files always use `status: ACTIVE`
5. **Multi-currency**: Record the currency as stated by the user, do not convert
6. **Keyword matching**: Prioritize precise keywords (e.g. "Shaxian" → Food), then broad keywords (e.g. "other" → Other)
7. **Account selection**: If user doesn't specify, default to `Alipay` (expense) or `CMB` (income)
8. **Transfer detection**: When trigger words like "transfer / send / allocate" are detected, you **must** follow the transfer workflow (create 2 files) — do NOT treat it as expense or income
9. **Pair ID consistency**: The `transfer_pair_id` in the out and in files **must be identical**, otherwise pair lookup will fail
10. **Pair ID uniqueness**: Use a fresh `T-{date}-{random-string}` for every transfer, to avoid clashes with historical data

---

## File Location Reference

```
Project root/
├── AGENTS.md                         ← This file (AI Agent guide)
├── Templates/                        ← Templater templates (human manual use)
│   ├── expense-template.md
│   ├── income-template.md
│   └── transfer-template.md
├── Transactions/                     ← Files created by AI Agent
│   ├── expenses/
│   ├── incomes/
│   └── transfers/
│       ├── out/                      ← Transfer-out files
│       └── in/                       ← Transfer-in files
├── Dashboards/
│   └── finance-dashboard.md          ← Dataview dashboard
├── Categories/
│   ├── expense-category-rules.md     ← Category rules for AI Agent
│   ├── income-category-rules.md
│   └── transfer-categories.md        ← Transfer category (Transfer only)
└── Accounts/
    └── account-list.md               ← Account definitions
```

---

## Related Files

- [[Finance Dashboard]] — View all transaction summaries
- [[Account List]] — Account balance queries
- [[Expense Categories]] — Full expense category descriptions
- [[Income Categories]] — Full income category descriptions
- [[Transfer Categories]] — Transfer category description
- [[expense-category-rules.md]] — Category keyword mapping (table format)
- [[income-category-rules.md]] — Income category keyword mapping (table format)
- [[transfer-categories.md]] — Transfer category keyword mapping (table format)

---

> For AI Agent use | Created: 2026-06-01 | Version: V1.0
