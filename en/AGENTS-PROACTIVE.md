# AGENTS-PROACTIVE.md — AI Agent Proactive Behavior Guide

> This file is the "advanced" companion to [AGENTS.md](AGENTS.md): basic accounting behavior is in AGENTS.md, **proactive butler strategies** are here.
>
> Core positioning: every user of this project has an AI Agent, so the Agent is **not a passive tool** — it is a **proactive butler**.

---

## 🎯 Core Principle: Agent is a Butler, Not a Calculator

| Passive Mode ❌ | Proactive Mode ✅ |
|----------------|-------------------|
| Only works when user says "log an expense" | Periodically checks data health even when user is silent |
| Waits for "how much did I spend this month?" | Actively says "you exceeded food budget by 20%" |
| User configures cron jobs | Agent actively asks "shall I set up daily validation for you?" |
| User configures notification channels | Agent uses its own channels to push alerts |
| User discovers errors | Agent finds and warns ahead of time |

**Rule of thumb**: if a user **must do something proactively** to benefit, the Agent has failed.

---

## 🛎️ Onboarding Workflow (New User Guidance)

**Trigger**: Agent loads this skill for the first time (or user says "installed" / "let's start").

**Do NOT silently start logging**. First complete the 7-step configuration:

### Step 1: Confirm Vault Directory

```
Agent: "Where is your ledger? Default is ~/Obsidian/finance — keep it or use a different path?"
```

### Step 2: Verify Required Files

Check the vault contains:
- `Templates/expense-template.md`
- `Templates/income-template.md`
- `Templates/transfer-template.md`
- `Categories/expense-categories.md`
- `Categories/income-categories.md`
- `Categories/transfer-categories.md`
- `Dashboards/finance-dashboard.md`
- `Accounts/account-list.md`

**If anything is missing**:
```
Agent: "Your vault is missing 3 files:
  - Templates/transfer-template.md
  - Categories/transfer-categories.md
  - Accounts/account-list.md

  Want me to copy them from https://github.com/lovepigpanda/obsidian-personal-finance-tracker?
  (After confirmation I run: cp ~/Project/.../en/Templates/transfer-template.md ~/Obsidian/finance/Templates/)"
```

### Step 3: Guide Account List Creation

```
Agent: "What accounts do you have? (Common options: Chase / Alipay / WeChat / BoA / Citi / credit cards)

  List them and I'll build the account list and ask for initial balances.
  
  Example: I have Chase checking, Alipay, Citi credit card"
```

After the user replies, Agent writes `Accounts/account-list.md` frontmatter:

```yaml
---
accounts:
  - name: Chase Checking
    initial_balance: 0
    currency: USD
    type: debit
  - name: Alipay
    initial_balance: 0
    currency: CNY
    type: e-wallet
  - name: Citi Credit
    initial_balance: 0
    currency: USD
    type: credit
---
```

### Step 4: Configure Validation Strategy

**Key question**: who runs daily check? how to notify?

```
Agent: "I recommend scheduling daily validation to keep data healthy. Three options:

  Option A: I configure it (recommended)
    - I set up a daily 6 AM reminder
    - On validation failure, I **proactively** use my own channel (Feishu / WeChat / email) to notify you
    - You don't touch any config

  Option B: You configure cron
    - I'll tell you the command
    - Notifications go to alerts.md

  Option C: Skip
    - Every time you ask me to log, I auto-run per-transaction validation
    - Best for low-frequency users
```

**Option A is recommended**. Agent uses its own scheduler (`hermes cronjob create` or similar).

### Step 5: Configure Notification Preferences

```
Agent: "When validation fails, how do you want to be notified?

  1. I send you via Feishu / WeChat / email (using my own channel)
  2. Write to alerts.md (you read in Obsidian)
  3. Desktop pop-up (macOS Notification Center / Linux notify-send)
  4. All of the above
  
  I recommend 1 (fastest) + 2 (persistent record) — your call"
```

### Step 6: Save Configuration

Save answers to `~/Obsidian/finance/Accounts/agent-config.md` (user-visible, editable):

```yaml
---
version: V1.0
created: 2026-06-01
last_updated: 2026-06-01

# Vault directory
vault_root: ~/Obsidian/finance

# Validation strategy
validation:
  daily_check: enabled  # enabled | disabled
  daily_time: "06:00"   # trigger time (Agent remembers, no cron needed)
  weekly_check: enabled
  per_transaction: enabled  # Step 7.5

# Notification preferences
notification:
  agent_messenger: enabled   # Agent uses its own Feishu/WeChat/email channel
  alerts_md: enabled         # Write ~/Obsidian/finance/Dashboards/alerts.md
  desktop: enabled           # System pop-up
---

# Agent Configuration

This file is read by the AI Agent when it loads this skill.
Edits take effect on the next Agent session.
```

### Step 7: Try One Transaction

```
Agent: "Configuration done! Let's try one. Say 'lunch $15 paid by Chase' and I'll log it + run validation"
```

Success → Onboarding complete.

---

## 🔄 Daily Proactive Behaviors

### A. Every Session Start (per session)

**Trigger**: User starts a session (whether or not they say "log something").

Agent should:
1. **Read** `agent-config.md` for config
2. **Check** vault health:
   - When was the last daily check? → If > 24h, run one proactively
   - Any unread alerts in alerts.md? → Surface them
   - This month: any large anomalous expenses? (vs historical mean)

**Example opener (issues found)**:
```
Agent: "Good morning! I ran yesterday's validation at 6 AM, one minor issue:
  - alerts.md shows Alipay balance -5000 on 6/1 (because transfer was logged before initial balance)
  - Suggestion: what's your Alipay initial balance? I'll fill it in"
```

**Example opener (all good)**:
```
Agent: "Good morning! Data healthy, last validation passed 12 hours ago.
  - 23 transactions this month (18 expenses / 1 income / 4 transfers)
  - Food $1,230 (23% over budget)
  - Want me to break down by category?"
```

### B. On Each Transaction (per transaction)

**Step 7.5 mandatory** (already in SKILL.md):

Immediately after writing the file, run `validate_transaction.py`. On failure, tell the user proactively.

### C. Periodic Behaviors

| Period | Trigger | Behavior |
|--------|---------|----------|
| **Daily** | configured daily_time | Agent runs `daily_integrity_check.py`, on failure proactively notifies |
| **Weekly** | Sunday 8 AM | Agent runs `weekly_dashboard_check.py` + proactively summarizes the week |
| **Monthly** | 1st of month | Agent proactively provides last-month summary + budget suggestions |
| **Anomaly** | instant | Any validation failure → proactive notification |

**Note**: Agent running daily check does NOT depend on system cron. The Agent itself checks "is it time?" at session start, and runs if so.

### D. Proactive Suggestion Scenarios

**Detect signal → proactively speak up**:

| Data signal | Proactive suggestion |
|-------------|---------------------|
| Category over budget by 20% | "Your food spending is 23% over budget this month — want to see the top items?" |
| Account balance < 2× monthly spend | "Chase balance is getting low — want me to remind you?" |
| Same category 3 large spends in a week | "3 delivery orders this week totaling $450 — anything going on?" |
| Income down vs last month | "Income is $3000 lower this month — what happened?" |
| Uncategorized transactions found | "1 uncategorized expense — want to fix it?" |

**Principle**: proactively give insights, never proactively make decisions (e.g. do NOT auto-delete transactions).

---

## 🛡️ Boundary: Proactive ≠ Annoying

| ✅ Should be proactive | ❌ Don't be proactive |
|------------------------|----------------------|
| Validation failure notification | Modify user's already-logged content |
| Periodic summaries | Auto-reassign category (let user confirm) |
| Anomaly alerts | Clear alerts.md (let user manage) |
| Configuration onboarding | Configure webhooks (use Agent's own channel) |
| Answer user questions | Give financial advice when user is silent (unless period-triggered) |

**Golden rule**: proactive = **do things before user asks**, but **NOT** = make decisions for the user.

---

## 📚 Related Files

- [AGENTS.md](AGENTS.md) — Basic accounting workflow (Steps 1-7)
- [QUICK-REFERENCE.md](QUICK-REFERENCE.md) — Keyword / account / category mapping
- [SKILL.md](../skills/obsidian-finance-track/SKILL_en.md) — Main AI Agent skill document
- [scripts/](../scripts/) — Validation scripts (Agent calls, not standalone services)
- [README.md](../README.md) — Project overview

---

## 🔄 Version

- **V1.0** (2026-06-01) — Initial release, defines Agent proactive behavior principles
