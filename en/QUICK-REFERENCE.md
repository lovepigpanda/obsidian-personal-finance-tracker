---
title: Finance Category Quick Reference — AI Agent
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: quick-reference
tags: [agent, finance, reference]
description: AI Agent quick lookup for categories and accounts (structured format)
---

# AI Agent Quick Reference (Structured)

> This file is for AI Agent programmatic reading. Provides category mapping, account mapping, and file format specifications.

---

## Expense Categories

| Category | English Name | Emoji | Keywords |
|----------|--------------|-------|----------|
| Food | Food | 🍔 | lunch, dinner, breakfast, takeout, restaurant, food, meal, snack, Shaxian, Lanzhou, fast food, canteen, early breakfast, midnight snack, BBQ, hotpot |
| Transport | Transport | 🚌 | subway, bus, taxi, uber, parking, gas, train, travel, DiDi, hitchhike, cycling |
| Shopping | Shopping | 🛍️ | Taobao, JD, Pinduoduo, shopping, clothes, shoes, supermarket, daily goods, store, electronics, phone |
| Entertainment | Entertainment | 🎮 | movie, game, music, video, iQIYI, Tencent Video, Steam, Netflix, subscription, KTV |
| Health | Health | 💊 | hospital, pharmacy, medicine, checkup, dental, TCM, clinic, medical, see doctor, registration |
| Education | Education | 📚 | course, tuition, book, training, exam, subscription, edu, learning, tutorial, extracurricular |
| Housing | Housing | 🏠 | rent, property, utilities, gas, repair, furniture, renovation, housekeeping, cleaning |
| Communication | Communication | 📱 | phone, mobile plan, broadband, data, communication, landline |
| Gift | Gift | 🎁 | red envelope, gift, treat, 人情, gift giving, 份子钱 |
| Travel | Travel | ✈️ | flight, hotel, travel, ticket, vacation, sightseeing, scenic spot |
| Investment | Investment | 💹 |理财, fund, stock, investment, loss |
| Other | Other | ❓ | other, miscellaneous |

## Income Categories

| Category | English Name | Emoji | Keywords |
|----------|--------------|-------|----------|
| Salary | Salary | 💰 | salary, monthly pay, wages, base salary, paycheck |
| Bonus | Bonus | 🎉 | year-end bonus, bonus, performance, dividend, annual award, quarterly bonus, project bonus |
| Freelance | Freelance | 💻 | freelance, side job, gig, contract work,自由职业, 接活 |
| Investment | Investment | 📈 | investment interest, fund dividend, stock gain, dividend, 理财利息 |
| Refund | Refund | 🔄 | refund, return, compensation, 赔偿 |
| Gift | Gift | 🎁 | red envelope, gift money, 礼金 |
| Other | Other | ❓ | other, incidental income |

## Account Mapping

| Account | Type | Keywords |
|---------|------|----------|
| Alipay | e-wallet | Alipay, 支付宝 |
| WeChat Pay | e-wallet | WeChat, WeChat Pay, 微信支付 |
| CMB | bank | CMB, China Merchants Bank, 招行, 招商银行 |
| ICBC | bank | ICBC, Industrial and Commercial Bank, 工行, 工商银行 |
| Credit Card | credit-card | Credit Card, 信用卡, 贷记卡 |
| Cash | cash | Cash, 现金 |
| USD Account | bank | USD Account, 美元账户 |

## Payment Methods

| Method | Keywords |
|--------|----------|
| Alipay | Alipay, 支付宝 |
| WeChat Pay | WeChat, WeChat Pay, 微信支付 |
| Bank Transfer | Bank Transfer, wire, 银行转账, 招行, 工行 |
| Credit Card | Credit Card, 信用卡 |
| Debit Card | Debit Card, 借记卡 |
| Cash | Cash, 现金 |

## Currencies

| Currency | Code | Keywords |
|----------|------|----------|
| Chinese Yuan | CNY | CNY, 元, 块, RMB |
| US Dollar | USD | USD, dollar, 美元, 刀 |
| Euro | EUR | EUR, euro, 欧元 |
| Japanese Yen | JPY | JPY, yen, 日元, 円 |
| Hong Kong Dollar | HKD | HKD, HK, 港币 |

## File Naming Convention (AI Generated Filenames)

### Expense Files
```
Transactions/expenses/{YYYY-MM-DD}-{description}-{amount}-{CURRENCY}-{STATUS}.md
```
Example: `Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

### Income Files
```
Transactions/incomes/{YYYY-MM-DD}-{description}-{amount}-{CURRENCY}-{STATUS}.md
```
Example: `Transactions/incomes/2026-06-01-salary-15000-CNY-ACTIVE.md`

## Frontmatter Template (AI Generated)

```yaml
---
type: expense                    # or income
date: YYYY-MM-DD
amount: number
currency: CNY                    # CNY/USD/EUR/JPY/HKD
category: CategoryName
account: AccountName
payment_method: PaymentMethod
note: "User's raw description"
tags: [expense, categoryName]    # expense or income + category name
status: ACTIVE
created: YYYY-MM-DD
---
```

## Date Conversion Rules

| User Input | Converts To |
|------------|-------------|
| today | Current date (2026-06-01) |
| yesterday | Current date - 1 day |
| the day before yesterday | Current date - 2 days |
| last week | Monday of this week |
| last month | 1st of last month |

## Amount Extraction Rules

| User Input | Extracts |
|------------|----------|
| "45 CNY" | amount=45, currency=CNY |
| "15000" | amount=15000, currency=CNY (default) |
| "35 USD" | amount=35, currency=USD |
| "€50" | amount=50, currency=EUR |
| "15000 CNY" | amount=15000, currency=CNY |
| "500 dollars" | amount=500, currency=USD |

---

## AI Agent Standard Workflow

```
1. Read user's natural language input
2. Identify type: expense ("spent","bought","paid","花","买") → expense
                   income ("received","got paid","salary","收到","进账") → income
3. Extract date: time words → YYYY-MM-DD
4. Extract amount + currency: number + currency
5. Match account: payment tool → account name
6. Match payment_method: same as account
7. Match category: keyword lookup in category table above
8. Generate filename: {date}-{description}-{amount}-{currency}-ACTIVE.md
9. Write to Transactions/expenses/ or Transactions/incomes/
10. Return completion info to user
```

---

## File Path Summary

| File | Path |
|------|------|
| Expense rules | `Categories/expense-category-rules.md` |
| Income rules | `Categories/income-category-rules.md` |
| Expense template | `Templates/expense-template.md` |
| Income template | `Templates/income-template.md` |
| Dashboard | `Dashboards/finance-dashboard.md` |
| Account list | `Accounts/account-list.md` |
| This file | `QUICK-REFERENCE.md` |

---

> For AI Agent use | Created: 2026-06-01