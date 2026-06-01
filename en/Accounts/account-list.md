---
title: Account List — Account Definitions
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: account-list
tags: [finance, accounts]
---

## Account Definitions

> Account balances are auto-calculated by Dataview (initial balance + income − expenses). No manual update needed.

| Account | Type | Currency | Initial Balance | Note | Status |
|---------|------|----------|-----------------|------|--------|
| Cash | cash | CNY | 0 | Cash | ACTIVE |
| Alipay | e-wallet | CNY | 0 | Alipay | ACTIVE |
| WeChat Pay | e-wallet | CNY | 0 | WeChat Pay | ACTIVE |
| CMB | bank | CNY | 0 | China Merchants Bank | ACTIVE |
| ICBC | bank | CNY | 0 | Industrial and Commercial Bank | ACTIVE |
| Credit Card | credit-card | CNY | 0 | Credit Card (negative = debt) | ACTIVE |
| USD Account | bank | USD | 0 | USD Account | ACTIVE |

---

## Real-time Balance Calculation

> Auto-calculated by Dataview, refreshes when file is opened

```dataviewjs
// All accounts
const accounts = ["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"];

// Initial balances (maintain manually)
const initialBalances = {
  "Cash": 0,
  "Alipay": 0,
  "WeChat Pay": 0,
  "CMB": 0,
  "ICBC": 0,
  "Credit Card": 0,
  "USD Account": 0
};

// Read all transaction files
const expenses = dv.pages('"Transactions/expenses"').filter(p => p.status === "ACTIVE");
const incomes = dv.pages('"Transactions/incomes"').filter(p => p.status === "ACTIVE");

// Calculate balance for each account
const results = [];
for (const account of accounts) {
  const expSum = expenses.filter(p => p.account === account).amount.sum() || 0;
  const incSum = incomes.filter(p => p.account === account).amount.sum() || 0;
  const balance = (initialBalances[account] || 0) + incSum - expSum;
  results.push({ account, balance });
}

// Output table
dv.table(["Account", "Current Balance"], results.map(r => [r.account, r.balance]));
```

---

## Adding a New Account

1. Add a row in the table above with account info
2. Add new account name to the initial balance map
3. It will automatically appear in Templater template account options

> Related: [[Finance Dashboard]] · [[Expense Categories]] · [[Income Categories]]