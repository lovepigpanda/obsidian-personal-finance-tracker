---
title: Finance Dashboard — Personal Finance Dashboard
created: 2026-06-01
updated: <% tp.date.now("YYYY-MM-DD") %>
version: V1.0
status: ACTIVE
type: dashboard
tags: [finance, dashboard]
---

# 💰 Personal Finance Dashboard

> Last updated: <% tp.date.now("YYYY-MM-DD HH:mm") %>

---

## This Month Overview

```dataview
table date, amount, category, account, note
from "Transactions/expenses"
where date >= 2026-06-01 and date <= 2026-06-30 and status = "ACTIVE"
sort date desc
limit 5
```

**This month expenses**: ```dataview
SELECT sum(amount) FROM "Transactions/expenses" WHERE date >= 2026-06-01 AND date <= 2026-06-30 AND status = "ACTIVE"
```

**This month income**: ```dataview
SELECT sum(amount) FROM "Transactions/incomes" WHERE date >= 2026-06-01 AND date <= 2026-06-30 AND status = "ACTIVE"
```

**This month balance**: ```dataview
SELECT (sum(i.amount) - sum(e.amount)) as balance FROM "Transactions/incomes" i, "Transactions/expenses" e WHERE i.date >= 2026-06-01 AND i.date <= 2026-06-30 AND e.date >= 2026-06-01 AND e.date <= 2026-06-30 AND i.status = "ACTIVE" AND e.status = "ACTIVE"
```

---

## Expense Category Breakdown

```dataview
table category, sum(amount) as total
from "Transactions/expenses"
where date >= 2026-06-01 and date <= 2026-06-30 and status = "ACTIVE"
group by category
sort total desc
```

---

## Income Category Breakdown

```dataview
table category, sum(amount) as total
from "Transactions/incomes"
where date >= 2026-06-01 and date <= 2026-06-30 and status = "ACTIVE"
group by category
sort total desc
```

---

## Account Balances

```dataviewjs
const accounts = ["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"];
const initialBalances = { "Cash": 0, "Alipay": 0, "WeChat Pay": 0, "CMB": 0, "ICBC": 0, "Credit Card": 0, "USD Account": 0 };

const expenses = dv.pages('"Transactions/expenses"').filter(p => p.status === "ACTIVE");
const incomes = dv.pages('"Transactions/incomes"').filter(p => p.status === "ACTIVE");
const transferOut = dv.pages('"Transactions/transfers/out"').filter(p => p.status === "ACTIVE");
const transferIn = dv.pages('"Transactions/transfers/in"').filter(p => p.status === "ACTIVE");

const results = [];
for (const account of accounts) {
  const expSum = expenses.filter(p => p.account === account).amount.sum() || 0;
  const incSum = incomes.filter(p => p.account === account).amount.sum() || 0;
  const outSum = transferOut.filter(p => p.from_account === account).amount.sum() || 0;
  const inSum = transferIn.filter(p => p.to_account === account).amount.sum() || 0;
  const balance = (initialBalances[account] || 0) + incSum - expSum - outSum + inSum;
  results.push({ account, balance });
}

dv.table(["Account", "Balance"], results.map(r => [r.account, r.balance.toFixed(2)]));
```

---

## This Month Transfers

```dataview
table date, from_account + " → " + to_account as "Flow", amount, currency, note
from "Transactions/transfers/out"
where date >= 2026-06-01 and date <= 2026-06-30 and status = "ACTIVE"
sort date desc
```

**This month total transfers out** (by currency): ```dataview
SELECT sum(amount) FROM "Transactions/transfers/out" WHERE date >= 2026-06-01 AND date <= 2026-06-30 AND status = "ACTIVE" GROUP BY currency
```

**This month total transfers in** (by currency): ```dataview
SELECT sum(amount) FROM "Transactions/transfers/in" WHERE date >= 2026-06-01 AND date <= 2026-06-30 AND status = "ACTIVE" GROUP BY currency
```

**Find pair:** In Obsidian global search `transfer_pair_id: T-2026-06-01-xxx`, you can locate both the out and in files at the same time.

---

## Recent Transactions

```dataview
table date, type, amount, category, account, note
from "Transactions"
where status = "ACTIVE"
sort date desc
limit 10
```

---

## Quick Actions

- [[Expense Template]] — Record new expense
- [[Income Template]] — Record new income
- [[Transfer Template]] — Record new transfer (paired dual files)
- [[Account List]] — View account balances
- [[Expense Categories]] — Expense category descriptions
- [[Income Categories]] — Income category descriptions
- [[Transfer Categories]] — Transfer category descriptions
