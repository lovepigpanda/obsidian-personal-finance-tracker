---
title: Transfer Categories — Transfer Category Definitions
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: category-list
tags: [finance, categories, transfer]
---

## Transfer Category List

| Category | English Name | Emoji | Description |
|----------|--------------|-------|-------------|
| 转账 | Transfer | 🔁 | Funds movement between accounts (not counted as income or expense) |

---

## Category Keyword Mapping Rules

| Keyword | Mapped Category |
|---------|-----------------|
| 转账, 转给, 打给, 转入, 转出, 转到, 来自, 调拨, 调头寸, 还信用卡, 还卡, 补仓, 充值, 提现, from, to | Transfer |

---

## Important Notes

**Transfer ≠ Income/Expense** — it is a movement of funds between accounts.

**Storage Method: Paired Double Files**
- Outgoing file: `Transactions/transfers/out/{date}-transfer-out-{from}-to-{to}-{amount}-{CCY}-ACTIVE.md`
- Incoming file: `Transactions/transfers/in/{date}-transfer-in-{to}-from-{from}-{amount}-{CCY}-ACTIVE.md`
- Pairing ID: Both files share the same `transfer_pair_id` to link them

**Account Balance Calculation Logic:**
- Outgoing account: Initial balance + Income − Expense − Transfer out
- Incoming account: Initial balance + Income − Expense + Transfer in
- Transfers are not included in "Total Expense" or "Total Income"

**Multi-Currency Transfers:**
- Outgoing and incoming default to the same currency
- Cross-currency transfers require the exchange rate to be noted at the outer layer (e.g. 1000 USD → 7200 CNY), but Dataview still aggregates by each currency

---

## How to Customize Categories

Transfer has only one category (Transfer) and does not need to be extended. If you need to distinguish the purpose of the transfer (e.g. paying off credit card, topping up position, weekly salary transfer), use the `note` field to record it.

> Related: [[Finance Dashboard]] · [[Expense Categories]] · [[Income Categories]]
