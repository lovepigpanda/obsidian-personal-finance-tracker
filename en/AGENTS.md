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

## AI Agent Operation Checklist

When the user asks to record a transaction, AI Agent should:

- [ ] **1. Identify intent**: Is it expense or income?
- [ ] **2. Extract date**: Convert "today / yesterday / the day before yesterday" to standard date format
- [ ] **3. Extract amount**: Number + currency (default CNY)
- [ ] **4. Extract account**: Payment tool → account name (see account mapping table)
- [ ] **5. Match category**: Match category based on note keywords (see category mapping table)
- [ ] **6. Generate filename**: `YYYY-MM-DD-{description}-{amount}-{CURRENCY}-ACTIVE.md`
- [ ] **7. Create file**: Write to `Transactions/expenses/` or `Transactions/incomes/`
- [ ] **8. Write frontmatter**: type / date / amount / currency / category / account / payment_method / note / tags / status
- [ ] **9. Write body**: Standard format table
- [ ] **10. Confirm completion**: Tell user the file path and main content

---

## Notes

1. **Date format**: Use `YYYY-MM-DD` consistently, e.g. `2026-06-01`
2. **Amount**: Pure number, no currency symbol (e.g. `45` not `¥45`)
3. **Description**: English or Pinyin, connected with `-` (e.g. `lunch`, `subway`, `salary`)
4. **File status**: New files always use `status: ACTIVE`
5. **Multi-currency**: Record the currency as stated by the user, do not convert
6. **Keyword matching**: Prioritize precise keywords (e.g. "Shaxian" → Food), then broad keywords (e.g. "other" → Other)
7. **Account selection**: If user doesn't specify, default to `Alipay` (expense) or `CMB` (income)

---

## File Location Reference

```
Project root/
├── AGENTS.md                         ← This file (AI Agent guide)
├── Templates/                        ← Templater templates (human manual use)
│   ├── expense-template.md
│   └── income-template.md
├── Transactions/                     ← Files created by AI Agent
│   ├── expenses/
│   └── incomes/
├── Dashboards/
│   └── finance-dashboard.md          ← Dataview dashboard
├── Categories/
│   ├── expense-category-rules.md     ← Category rules for AI Agent
│   └── income-category-rules.md
└── Accounts/
    └── account-list.md               ← Account definitions
```

---

## Related Files

- [[Finance Dashboard]] — View all transaction summaries
- [[Account List]] — Account balance queries
- [[Expense Categories]] — Full expense category descriptions
- [[Income Categories]] — Full income category descriptions
- [[expense-category-rules.md]] — Category keyword mapping (table format)
- [[income-category-rules.md]] — Income category keyword mapping (table format)

---

> For AI Agent use | Created: 2026-06-01 | Version: V1.0