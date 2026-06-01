# Obsidian Personal Finance Tracker

A **personal finance tracking system** built with Obsidian (income + expense + account balance), where each transaction is stored as a single `.md` file. Powered by Dataview dashboards, supports multi-currency, multi-account, and automatic category mapping.

---

## ✨ Features

- ✅ **Expense tracking** — amount / category / account / payment method / note
- ✅ **Income tracking** — amount / source category / account / note
- ✅ **Multi-account balance tracking** — auto-calculated (initial balance + income − expenses)
- ✅ **Multi-currency separate display** — CNY / USD / EUR shown separately, no conversion
- ✅ **Automatic category mapping** — keyword input auto-suggests categories
- ✅ **Monthly summary reports** — auto-generated via Dataview
- ✅ **Main dashboard** — monthly balance / category breakdown / trends
- 🤖 **AI Agent support** — natural language accounting, auto-creates transaction files (see `AGENTS.md`)
- 📅 **Multi-currency exchange rates** (v1.1)
- 🏦 **Bank API auto-sync** (v2.0)

---

## 🤖 AI Agent Usage

This system is primarily designed for **AI Agents** (Claude / Hermes / etc.). The user describes a transaction in natural language, and the AI Agent automatically:

1. Parses intent (expense/income), date, amount, currency
2. Matches account and category (using `QUICK-REFERENCE.md` mapping tables)
3. Creates the corresponding `.md` file under `Transactions/`

**Example:**

User → `"Lunch at Shaxian spent 45 CNY, paid via Alipay"`

AI Agent → Auto-creates `Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

See: [AGENTS.md](zh/AGENTS.md) · [QUICK-REFERENCE.md](zh/QUICK-REFERENCE.md)

---

## 📁 Project Structure

```
obsidian-personal-finance-tracker/
├── LICENSE
├── README.md                       # Bilingual entry point
├── zh/                             # 🌏 Chinese version (primary)
│   ├── AGENTS.md                   # 🤖 AI Agent guide (core)
│   ├── QUICK-REFERENCE.md          # 📋 AI Agent quick reference
│   ├── Templates/
│   ├── Transactions/
│   ├── Dashboards/
│   ├── Accounts/
│   └── Categories/
├── en/                             # 🌎 English version
│   ├── AGENTS.md                   # 🤖 AI Agent guide
│   ├── QUICK-REFERENCE.md          # 📋 AI Agent quick reference
│   ├── Templates/
│   ├── Transactions/
│   ├── Dashboards/
│   ├── Accounts/
│   └── Categories/
└── Scripts/
```

---

## 🚀 Quick Start

### AI Agent Integration (Recommended)

1. Clone this repo to local (or copy files to your Obsidian vault)
2. AI Agent reads `zh/AGENTS.md` for workflow
3. AI Agent references `zh/QUICK-REFERENCE.md` for category/account lookups
4. User describes transactions in natural language, AI Agent creates files

### Manual Human Entry

1. Install **Dataview** and **Templater** plugins in Obsidian
2. Copy `zh/Templates/`, `zh/Dashboards/`, `zh/Accounts/`, `zh/Categories/` to your vault
3. Use Templater → New Note → select `expense-template.md` or `income-template.md`
4. Open `zh/Dashboards/finance-dashboard.md` to view financial overview

---

## 📖 AI Agent Workflow

```
User natural language → AI Agent parses → Match category/account → Create md file → Dashboard auto-updates
```

AI Agent steps:

1. **Identify type**: expense keywords ("spent","bought","paid") → `expense`; income keywords ("received","got paid","salary") → `income`
2. **Extract date**: "today" → `2026-06-01`, "yesterday" → `2026-05-31`
3. **Extract amount + currency**: "45 CNY" → `amount=45, currency=CNY`
4. **Match account**: payment tool → `Alipay` / `WeChat Pay` / `CMB` / etc.
5. **Match category**: keyword lookup in `QUICK-REFERENCE.md` category table
6. **Generate filename**: `{date}-{description}-{amount}-{currency}-ACTIVE.md`
7. **Create file**: write to `Transactions/expenses/` or `Transactions/incomes/`

---

## 🛠️ Plugin Dependencies (Manual Entry)

| Plugin | Required | Note |
|--------|----------|------|
| Dataview | ✅ | Query & render dashboards |
| Templater | ✅ | Interactive entry templates (human use) |
| Commander | ❌ | Quick commands (optional) |
| Obsidian Charts | ❌ | Trend charts (optional) |

---

## 📋 AI Agent Quick Reference

### Expense Categories

| Category | Keywords |
|----------|----------|
| Food 🍔 | lunch, dinner, breakfast, takeout, restaurant, food, snack, Shaxian, hotpot, BBQ |
| Transport 🚌 | subway, bus, taxi, uber, parking, gas, train, travel, DiDi |
| Shopping 🛍️ | Taobao, JD, Pinduoduo, shopping, clothes, shoes, supermarket, electronics, phone |
| Entertainment 🎮 | movie, game, music, video, iQIYI, Tencent Video, Steam, Netflix, subscription, KTV |
| Health 💊 | hospital, pharmacy, medicine, checkup, dental, clinic, medical |
| Education 📚 | course, tuition, book, training, exam, subscription, edu, learning, tutorial |
| Housing 🏠 | rent, property, utilities, gas, repair, furniture, renovation, cleaning |
| Communication 📱 | phone, mobile plan, broadband, data, SIM |
| Gift 🎁 | red envelope, gift, treat,人情, gift giving |
| Travel ✈️ | flight, hotel, travel, ticket, vacation, sightseeing |
| Investment 💹 |理财, fund, stock, investment, loss |
| Other ❓ | other, miscellaneous |

### Income Categories

| Category | Keywords |
|----------|----------|
| Salary 💰 | salary, monthly pay, wages |
| Bonus 🎉 | year-end bonus, bonus, performance, dividend |
| Freelance 💻 | freelance, side job, gig, contract work |
| Investment 📈 | investment interest, fund dividend, stock gain, dividend |
| Refund 🔄 | refund, return, compensation |
| Gift 🎁 | red envelope, gift money |
| Other ❓ | other, incidental income |

### Accounts

| Account | Keywords |
|---------|----------|
| Alipay | Alipay |
| WeChat Pay | WeChat, WeChat Pay |
| CMB | CMB, China Merchants Bank |
| ICBC | ICBC, Industrial and Commercial Bank |
| Credit Card | Credit Card |
| Cash | Cash |
| USD Account | USD Account |

---

## ⚠️ Known Limitations

1. Multi-currency exchange rates require manual maintenance (v1.1 plans auto-fetch)
2. Account balances are calculated in real-time by Dataview; initial balances must be set in `zh/Accounts/account-list.md`
3. China bank APIs not yet supported; auto-sync deferred (v2.0)

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

## 📄 License

MIT License