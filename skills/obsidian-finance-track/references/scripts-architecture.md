# Validation Scripts — Architecture Reference

This document is the source of truth for the `scripts/` design. Future agents extending
or debugging the validation tooling should read this first.

---

## Design Principles

1. **Zero external dependencies** — pure Python 3.8+ standard library. Any user on any
   platform (macOS, Linux, Windows) with any AI Agent (Hermes, OpenHuman, OpenClaw,
   Claude Code) can run them. No `pip install`.
2. **Three entry points, one shared lib** — the three CLI scripts are thin wrappers
   that import from `lib/`. All real logic lives in `lib/`.
3. **Path A == Path B for balance calculation** — both DataviewJS in
   `Dashboards/finance-dashboard.md` AND Python in `lib/balance.py` use the same
   algorithm: `final = initial + sum(income) - sum(expense) - sum(transfer_out) + sum(transfer_in)`.
   This is the **core guarantee**: the project's own two calculation paths can never
   disagree, because they share the same formula.
4. **Soft alert, never hard block** — all checks write to `alerts.md` and surface
   problems; none abort a transaction write. The user (or AI Agent) decides what to do
   with a warning. See `~/.hermes/USER.md` for the rationale (误判成本高).

---

## File Layout

```
scripts/
├── lib/                       # Shared library (imported, not run directly)
│   ├── __init__.py            # Package marker
│   ├── parsers.py             # Frontmatter parser + transfer-pair detector
│   ├── balance.py             # Balance calculation core (Path A/B shared formula)
│   └── notifier.py            # Notification dispatcher (alerts.md + desktop + webhook)
├── validate_transaction.py    # Per-transaction check (run by AI Agent on every write)
├── daily_integrity_check.py   # Daily conservation check (run by cron/launchd)
└── weekly_dashboard_check.py  # Weekly structure check (run by cron/launchd)
```

### `lib/parsers.py` — Frontmatter & Pair Detection

**Public API**:
- `parse_frontmatter(path) -> dict | None` — reads YAML frontmatter, returns dict.
  Returns `None` on parse error.
- `find_transfer_pair(from_dir, from_account, to_account, pair_id) -> Path | None` —
  given one end of a transfer, find the matching other end.
- `validate_filename(name, type) -> list[str]` — checks filename follows the project
  convention (`{date}-{...}-{amount}-{CURRENCY}-ACTIVE.md`).

**Conventions**:
- Never raise exceptions out of parsers. Return None / empty list. The CLI scripts
  decide how to format errors.
- Always read the file once. Don't reload on each call.

### `lib/balance.py` — Balance Calculation Core

**Public API**:
- `compute_balance(account_file, transactions_dir, currency) -> Decimal` — given
  an `Accounts/{account}.md` file with `initial_balance` frontmatter, and the
  transactions directory, return the final balance for the given currency.
- `compute_all_balances(accounts_dir, transactions_dir) -> dict[str, dict[str, Decimal]]` —
  compute for every account × every currency.

**Algorithm** (shared with DataviewJS):
```
final_balance(account, currency) =
    initial_balance(account, currency)
    + sum(income.where(account=account, currency=currency))
    - sum(expense.where(account=account, currency=currency))
    - sum(transfer_out.where(from_account=account, currency=currency))
    + sum(transfer_in.where(to_account=account, currency=currency))
```

**Why this is the only correct formula**:
- `expense.account` = account that paid → subtract from that account
- `income.account` = account that received → add to that account
- `transfer.from_account` = account that paid out → subtract (this is the "out" file)
- `transfer.to_account` = account that received → add (this is the "in" file)
- Transfers record 2 files but each file contributes exactly once to exactly one
  account's balance. The pair cancels out across the system (one +, one −).

### `lib/notifier.py` — Notification Dispatcher

**Public API**:
- `notify(title, body, level) -> None` — fan out to all enabled channels.

**Channels** (all enabled by default, env vars disable):
- `alerts.md` write to `~/Obsidian/finance/Dashboards/alerts.md` (always)
- Desktop notification: macOS `osascript`, Linux `notify-send` (always)
- Webhook (only if env var set):
  - `BARK_KEY` → Bark
  - `PUSHPLUS_TOKEN` → PushPlus
  - `SCT_KEY` → Server酱
  - `OBSIDIAN_FINANCE_WEBHOOK_URL` → generic

**Output format for `alerts.md`**:
```markdown
# 校验告警 — {ISO date}

## {level}: {title}
- **时间**: {ISO timestamp}
- **来源**: {script_name}
- **详情**: {body}

---
```

Append-only; do not rewrite historical entries. Users may have annotations.

### `validate_transaction.py` — Per-Transaction Check

**When to call**: AI Agent writes a new transaction file → call this BEFORE telling
the user "done". This is the **Step 7.5** in SKILL.md.

**Exit codes**:
- `0` = pass, silent continue
- `1` = fail, soft alert (file kept, agent asks user: fix / ignore / delete)
- `2` = file not found / arg error

**Checks performed**:
1. Required frontmatter fields present (type, date, amount, currency, account|from_account|to_account, status)
2. `amount > 0`
3. `date` parses as YYYY-MM-DD
4. `currency` is in the known set
5. Account(s) registered in `~/Obsidian/finance/Accounts/account-list.md`
6. If `type == transfer`:
   - `transfer_pair_id` is set
   - Pair file exists (find via `find_transfer_pair`)
   - Pair file's `amount`, `currency`, `from_account`, `to_account` exactly match
   - `direction` matches the directory (`out/` → `direction: out`, `in/` → `direction: in`)

### `daily_integrity_check.py` — Daily Conservation Check

**When to call**: system cron / launchd at user's chosen time (default 6am).

**Checks**:
1. Every transfer is paired (no orphan out or in)
2. Pair file consistency (amount, currency, from, to match)
3. **Conservation**: for each currency, `sum(transfer_out) == sum(transfer_in)` —
   no money created/destroyed
4. **Self-consistency**: `compute_balance()` from `lib/balance.py` matches
   per-account `current_balance` in `Accounts/{account}.md` (if present)
5. Overdraft warning: any account with negative balance (soft alert)

**Output**: writes to `alerts.md`, exits non-zero if any ERROR-level issue found.

### `weekly_dashboard_check.py` — Weekly Structure Check

**When to call**: system cron, weekly (e.g. Sunday midnight).

**Checks**:
1. `Dashboards/finance-dashboard.md` exists and is parseable
2. Dashboard references all required Dataview fields
3. `Accounts/account-list.md` exists with all registered accounts
4. Print authoritative balance from `lib/balance.py` to stdout for user to
   visually compare with Dataview display

---

## When Extending the Scripts

### Adding a new check to `validate_transaction.py`
1. Implement the check function in `lib/` (keep `validate_transaction.py` thin)
2. Add it to the orchestrator in `validate_transaction.py`
3. Update `references/development-pitfalls.md` if the check reveals a new pitfall
4. Update SKILL.md "步骤 7.5" if the user-facing behavior changes

### Adding a new script
1. Create it under `scripts/` (not `scripts/lib/` — `lib/` is library-only)
2. If it needs shared logic, add it to `lib/` first
3. Add a section to this file (above) explaining the script's role, exit codes, and
   what checks it performs
4. Update README.md and SKILL.md

### Adding a new notification channel
1. Add a function in `lib/notifier.py` (e.g. `send_to_slack()`)
2. Wire it into the `notify()` dispatcher with an env-var guard
3. Document the env var in SKILL.md and README.md

### Refactoring the balance formula
**Do not.** The current formula in `lib/balance.py` is the canonical Path A/B
shared formula. DataviewJS in `finance-dashboard.md` is **required** to match.
Any change to the formula must update BOTH the Python and the DataviewJS in the
same commit, with verification that they still match.

---

## Cross-Reference

- `references/development-pitfalls.md` — historical bugs in the validation code
- SKILL.md 步骤 7.5 — the user-facing workflow that calls `validate_transaction.py`
- SKILL.md "校验脚本" section — same content, user-facing view
