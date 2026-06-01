---
title: Finance Dashboard — 个人财务仪表盘
created: 2026-06-01
updated: <% tp.date.now("YYYY-MM-DD") %>
version: V1.0
status: ACTIVE
type: dashboard
tags: [finance, dashboard]
---

# 💰 个人财务仪表盘

> 最后更新：<% tp.date.now("YYYY-MM-DD HH:mm") %>

---

## 本月概要

```dataview
table date, amount, category, account, note
from "Transactions/expenses"
where date >= 2026-06-01 and date <= 2026-06-30 and status = "ACTIVE"
sort date desc
limit 5
```

**本月支出**：```dataview
SELECT sum(amount) FROM "Transactions/expenses" WHERE date >= 2026-06-01 AND date <= 2026-06-30 AND status = "ACTIVE"
```

**本月收入**：```dataview
SELECT sum(amount) FROM "Transactions/incomes" WHERE date >= 2026-06-01 AND date <= 2026-06-30 AND status = "ACTIVE"
```

**本月余额**：```dataview
SELECT (sum(i.amount) - sum(e.amount)) as balance FROM "Transactions/incomes" i, "Transactions/expenses" e WHERE i.date >= 2026-06-01 AND i.date <= 2026-06-30 AND e.date >= 2026-06-01 AND e.date <= 2026-06-30 AND i.status = "ACTIVE" AND e.status = "ACTIVE"
```

---

## 支出分类分布

```dataview
table category, sum(amount) as total
from "Transactions/expenses"
where date >= 2026-06-01 and date <= 2026-06-30 and status = "ACTIVE"
group by category
sort total desc
```

---

## 收入分类分布

```dataview
table category, sum(amount) as total
from "Transactions/incomes"
where date >= 2026-06-01 and date <= 2026-06-30 and status = "ACTIVE"
group by category
sort total desc
```

---

## 各账户当前余额

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

dv.table(["账户", "余额"], results.map(r => [r.account, r.balance.toFixed(2)]));
```

---

## 本月转账

```dataview
table date, from_account + " → " + to_account as "流向", amount, currency, note
from "Transactions/transfers/out"
where date >= 2026-06-01 and date <= 2026-06-30 and status = "ACTIVE"
sort date desc
```

**本月转出总额**（按币种）：```dataview
SELECT sum(amount) FROM "Transactions/transfers/out" WHERE date >= 2026-06-01 AND date <= 2026-06-30 AND status = "ACTIVE" GROUP BY currency
```

**本月转入总额**（按币种）：```dataview
SELECT sum(amount) FROM "Transactions/transfers/in" WHERE date >= 2026-06-01 AND date <= 2026-06-30 AND status = "ACTIVE" GROUP BY currency
```

**查询配对：** 在 Obsidian 全局搜索 `transfer_pair_id: T-2026-06-01-xxx`，可同时定位 out 和 in 两个文件。

---

## 最近交易

```dataview
table date, type, amount, category, account, note
from "Transactions"
where status = "ACTIVE"
sort date desc
limit 10
```

---

## 快速操作

- [[Expense Template]] — 记录新支出
- [[Income Template]] — 记录新收入
- [[Transfer Template]] — 记录新转账（双文件配对）
- [[Account List]] — 查看账户余额
- [[Expense Categories]] — 支出分类说明
- [[Income Categories]] — 收入分类说明
- [[Transfer Categories]] — 转账分类说明