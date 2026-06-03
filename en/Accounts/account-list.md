---
title: Account List — Account Definitions
created: 2026-06-01
updated: 2026-06-03
version: V1.3
status: ACTIVE
type: account-list
tags: [finance, accounts]
---

## Account Definitions

> Account balances are pre-computed daily by `scripts/daily_integrity_check.py` and written to `Accounts/balances.md`. Dataview reads the snapshot (O(1) lookup). Initial balances are maintained manually in the table below.

| Account | Type | Currency | Initial Balance | Statement Day | Due Day | Principal | Monthly Payment | Payment Day | Total Months | Remaining Months | Start Month | Note | Status |
|---------|------|----------|-----------------|---------------|---------|-----------|-----------------|-------------|--------------|------------------|-------------|------|--------|
| Cash | cash | CNY | 0 | - | - | - | - | - | - | - | - | Cash | ACTIVE |
| Alipay | e-wallet | CNY | 0 | - | - | - | - | - | - | - | - | Alipay | ACTIVE |
| WeChat Pay | e-wallet | CNY | 0 | - | - | - | - | - | - | - | - | WeChat Pay | ACTIVE |
| CMB | bank | CNY | 0 | - | - | - | - | - | - | - | - | China Merchants Bank | ACTIVE |
| ICBC | bank | CNY | 0 | - | - | - | - | - | - | - | - | Industrial and Commercial Bank | ACTIVE |
| Credit Card | credit-card | CNY | 0 | 5 | 25 | - | - | - | - | - | - | Credit Card (negative = debt) | ACTIVE |
| USD Account | bank | USD | 0 | - | - | - | - | - | - | - | - | USD Account | ACTIVE |
| Mortgage | loan | CNY | -1000000 | - | - | 1000000 | 8500 | 31 | 240 | 240 | 2024-01 | Mortgage example: 30 years, payment day 31 (1月 has it, 2/4/6/9/11 auto-use 30/28), total 240 | ACTIVE |

> **Credit Card note**: Statement Day is when bill is issued, Due Day is the last day to pay (typically 20 days after statement). `#23` proactive reminder depends on these two fields.
> Example (CMB): Statement Day 5, Due Day 25.
> When adding a credit card account, **must** fill Statement Day + Due Day, otherwise no reminder.

> **Loan account note** (V1.3): Type is `loan`, balance **should be** negative (= unpaid principal). `#37` proactive reminder depends on these 5-6 fields.
>
> **Required 5 fields** (script needs all 5 to compute reminders):
> 1. **Principal** — float, original loan amount
> 2. **Monthly Payment** — float, amount to pay each month
> 3. **Payment Day** — int 1-31, **actual** debit day (not hard-coded "month end", script auto-handles short months: 2月 → 28/29, 30-day months → 30)
> 4. **Total Months** / **Term Months** — int, contract total period
> 5. **Start Month** — YYYY-MM format, the month of the **first** payment
>
> **Optional 1 field** (for consistency check only):
> 6. **Remaining Months** — int, how many months left from today
>
> `#37` loan payment reminder depends on these 5-6 fields. **Incomplete = no reminder** (only INFO reported).
>
> To make a payment = create a regular expense transaction with `account=loan account name`, `amount=monthly payment`. The script scans the current month's expenses to auto-detect "paid or not" — same logic as credit card, no special tracking field needed.
>
> **Consistency check** (if Remaining Months is filled): `paid_periods (from expense count) + remaining_months == total_months` — if not equal, WARN (data stale).
>
> When adding a loan account, **must** fill the 5 required fields, otherwise `#37` will not remind (only INFO field-missing).

---

## Real-time Balance Calculation

> Pre-computed snapshot written to `Accounts/balances.md` by `scripts/daily_integrity_check.py` (daily 18:00 cron). Dataview reads snapshot, O(1) lookup.

```dataview
table Current_Balance as "Current Balance", Last_Updated as "Last Updated"
from "Accounts/balances"
```

---

## Adding a New Account

1. Add a row in the table above with account info
2. **Loan accounts**: must fill 5 required fields (Principal / Monthly Payment / Payment Day / Total Months / Start Month)
3. **Credit card accounts**: must fill Statement Day + Due Day
4. Daily 18:00 cron auto-recomputes snapshot in `Accounts/balances.md`
5. Dataview dashboard auto-reflects on next open

> Related: [[Finance Dashboard]] · [[Expense Categories]] · [[Income Categories]]
