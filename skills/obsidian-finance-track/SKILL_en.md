---
name: obsidian-finance-track
tagline: 你的 AI 理财搭档 · Your AI Finance Partner
description: >
  Obsidian Personal Finance Tracking AI Agent Skill. Load this skill when the user describes
  accounting-related content (expenses, income, transfers, wallet balance, salary, shopping, etc.)
  or explicitly uses trigger words like "记账" (record), "记一笔" (log one), "花了多少" (how much spent),
  "收到" (received), "转给 X" (transfer to X), etc.

  Supports Chinese and English users, automatically parses natural language input, creates
  transaction .md files in the Obsidian vault, and updates Dataview dashboards.

  ⚠️ Skill code is separated from ledger data: skills come from GitHub sync, ledger data is
  stored locally at ~/Obsidian/finance/
  See the "Data Storage Architecture" section for details.

  🚨 First-load mandatory gate: when the user says "I'm set up" / "let's start" /
  "set up bookkeeping" / "initialize" etc., or when the vault directory is missing
  `Accounts/agent-config.md`, the Agent **MUST** immediately execute the "Onboarding
  7 steps". Do NOT proceed to bookkeeping. Incomplete Onboarding = skill not truly enabled.
triggers:
  # === Initialization triggers (first-time use) ===
  - 装好了
  - 开始用
  - 初始化
  - 设置记账
  - 配置记账
  - onboard
  - setup
  - initialize
  # === Bookkeeping triggers ===
  - 记账
  - 记一笔
  - 花了
  - 买了
  - 支出
  - 收入
  - 收到钱
  - 工资
  - 消费
  - 转账
  - 转给
  - 转到
  - 打给
  - 还信用卡
  - 调拨
  - 充值
  - 提现
  - expense
  - income
  - transfer
  - spent
  - paid
  - received
  - 午餐
  - 晚餐
  - 支付宝
  - 微信支付
  - 银行卡
  - 报销
  - 退款
  - 红包
  - balance
  - 余额
  - 账户
version: V1.2
status: ACTIVE
tags: [finance, obsidian, accounting, agent, nlp]
author: lovepigpanda
github: https://github.com/lovepigpanda/obsidian-personal-finance-tracker
---

# Obsidian Finance Track — AI Agent Accounting Skill

> This skill enables the AI Agent to perform natural language accounting: parse user input →
> match categories/accounts → create transaction .md files → update dashboard

---

## 🚨 Mandatory Gate: Onboarding Status Check (AI Agent MUST read)

**First thing after loading this Skill** — before any bookkeeping operation:

```python
# Pseudo-code: any agent MUST run this after loading the skill
vault = os.path.expanduser("~/Obsidian/finance")
config_file = os.path.join(vault, "Accounts/agent-config.md")

if not os.path.exists(config_file):
    # ⚠️ Sentinel missing = not initialized
    print("⚠️ First-time use detected, Onboarding required")
    # Jump immediately to "Step 0: Onboarding" section below
    # Do NOT execute any bookkeeping/validation/summary operations
else:
    # Already initialized, proceed normally
    pass
```

**Why this is mandatory**:

| Situation | Consequence |
|-----------|-------------|
| User books transactions without Onboarding | Empty account list → validation fails; no scheduled tasks → Agent can't proactively remind; user misses #23–#36 features |
| Onboarding done but skipped scheduled tasks | Agent can only "passively wait for user sessions", no out-of-session notifications (violates Agent-as-butler positioning) |
| **Onboarding 7 steps = required to enable this Skill**, not optional | Any agent skipping Onboarding = this load counts as a failure |

**Onboarding completion criterion**: `Accounts/agent-config.md` exists and contains `onboarded: true` field.

**How can a user who already finished Onboarding re-access config?** — Just say "reconfigure" / "redo Onboarding", the agent should walk the 7 steps again (**back up the existing config first**).

---

## Data Storage Architecture ⚠️ Required Reading

**Skill code and ledger data are completely separated** — this is the core design principle:

```
GitHub Repository                        Local Obsidian Vault (private, never upload)
─────────────────                          ─────────────────────────────
obsidian-personal-finance-tracker         ~/Obsidian/finance/
├── skills/                              ← Skill code, synced from GitHub
│   └── obsidian-finance-track/
├── zh/                                  ← Templates, rules, docs (distributable)
│   ├── AGENTS.md                        ← AI Agent workflow
│   ├── Templates/                       ← Templater template files
│   ├── Categories/                      ← Category rules
│   └── Dashboards/                      ← Dataview dashboard templates
└── README.md                            ← Project documentation

                                      ~/Obsidian/finance/
                                      ├── Templates/             ← Local copies (user customization)
                                      ├── Categories/            ← Local copies (user customization)
                                      ├── Dashboards/            ← Local copies (user customization)
                                      ├── Accounts/              ← Account list (with balances)
                                      ├── Transactions/          ← ⭐ Your actual ledger data
                                      │   ├── expenses/          ← One .md file per expense
                                      │   ├── incomes/           ← One .md file per income
                                      │   └── transfers/         ← Two .md files per transfer (out+in paired)
                                      │       ├── out/           ← Transfer-out files
                                      │       └── in/            ← Transfer-in files
                                      └── SKILL.md              ← Local skill copy
```

### Why This Design?

| Item | GitHub Project (Skill) | Local Vault (Data) |
|------|------------------------|---------------------|
| Content | Templates, rules, scripts, documentation | Your actual transaction records |
| Sync | `git pull` to update from GitHub | Never upload, private |
| Customization | Can submit PRs to improve shared rules | User's own accounts, notes |
| Risk | Accidental operations won't affect ledger data | Ledger data fully isolated |

### Update Process

```bash
# 1. Update skill code (pull latest templates/rules from GitHub)
git -C ~/Project/obsidian-personal-finance-tracker pull

# 2. To sync new templates to local vault, manually copy
cp ~/Project/obsidian-personal-finance-tracker/zh/Templates/* ~/Obsidian/finance/Templates/

# 3. Ledger data (~/Obsidian/finance/Transactions/) needs no action, fully autonomous
```

---

## Local Vault Path

```
~/Obsidian/finance/
```

**Directory Structure:**

```
~/Obsidian/finance/
├── Templates/                     ← Templater templates (auto-invoked by Templater plugin)
│   ├── expense-template.md        ← Expense record template
│   ├── income-template.md         ← Income record template
│   └── transfer-template.md       ← Transfer record template (paired dual files)
├── Categories/                    ← Category rules (read by AI Agent)
│   ├── expense-categories.md      ← Expense category descriptions
│   ├── expense-category-rules.md  ← Expense keyword mappings
│   ├── income-categories.md       ← Income category descriptions
│   ├── income-category-rules.md  ← Income keyword mappings
│   └── transfer-categories.md     ← Transfer category (Transfer only)
├── Dashboards/                    ← Dataview dashboards
│   └── finance-dashboard.md       ← Main dashboard
├── Accounts/                      ← Account list
│   └── account-list.md            ← Account names + initial balances
├── Transactions/                  ← ⭐ Actual ledger data (local, private)
│   ├── expenses/                  ← One .md file per expense
│   │   └── YYYY-MM-DD-*-ACTIVE.md
│   ├── incomes/                   ← One .md file per income
│   │   └── YYYY-MM-DD-*-ACTIVE.md
│   └── transfers/                 ← Two .md files per transfer (out+in share transfer_pair_id)
│       ├── out/                   ← Transfer-out files
│       └── in/                    ← Transfer-in files
```

---

## How It Works

```
User natural language input
       ↓
AI Agent reads ~/Obsidian/finance/Categories/*.md (category rules)
       ↓
Parse fields: type / date / amount / currency / category / account / note
       ↓
Determine type:
  - expense  → Write to ~/Obsidian/finance/Transactions/expenses/
  - income   → Write to ~/Obsidian/finance/Transactions/incomes/
  - transfer → Create 2 files (out + in), share transfer_pair_id
       ↓
Dataview dashboard (~/Obsidian/finance/Dashboards/finance-dashboard.md) auto-updates
```

---

## Trigger Conditions

Load this skill when ANY of the following conditions are met:

1. **Explicit triggers**: 记账 (record), 记一笔 (log one), 花 (spent), 买 (bought), 支出 (expense), 收入 (income), 收到 (received), 工资 (salary), 消费 (consume), 转账 (transfer)
2. **Financial keywords**: 支付宝 (Alipay), 微信支付 (WeChat Pay), 银行卡 (bank card), 报销 (reimbursement), 退款 (refund), 红包 (red envelope), 余额 (balance), 转给 (transfer to), 还信用卡 (pay credit card)
3. **English keywords**: expense, income, transfer, spent, paid, received, salary, budget
4. **Intent detection**: User describes money flowing in or out (regardless of wording)

---

## 🎯 Agent Positioning: Proactive Butler, Not Passive Tool

**Core positioning of this project**: everyone using it has an AI Agent, so the Agent is **not a calculator — it's a butler**.

| Passive ❌ | Proactive ✅ |
|---------|---------|
| Only works when user says "log something" | Actively checks data health at session start |
| Waits for "how much did I spend this month?" | Proactively says "you exceeded food budget by 20%" |
| User configures cron / launchd | **Agent actively asks** "shall I set up daily validation?" |
| User configures webhook notification | **Agent uses its own channel** to push proactively |
| Waits for user to find errors | Detects and warns ahead of time |

**Rule of thumb**: if a user **must do something proactively** to benefit, the Agent has failed.

---

## 🚀 Step 0: Onboarding (New User Guidance)

**Trigger**: User loads this skill for the first time (or says "installed" / "let's start").

**Do NOT silently start logging**. First complete the 7-step configuration (full content in [AGENTS-PROACTIVE.md](../../en/AGENTS-PROACTIVE.md)):

1. **Confirm vault directory** — default `~/Obsidian/finance`, confirm or change
2. **Verify required files** — check Templates / Categories / Dashboards / Accounts exist, proactively cp missing ones
3. **Guide filling account list** — ask "what accounts do you have", help write `Accounts/account-list.md` (ask credit card accounts for statement day / payment due day)
4. **Configure scheduled reminders** — **Core!** Proactively ask "shall I help you set up these scheduled tasks?" (Agent will **help generate** plist/cron, user just copies & pastes):
   - **Daily 18:00** run daily_integrity_check.py (includes #33 bookkeeping frequency, #34 account inactivity detection)
   - **Sunday 20:00** run weekly_summary.py (#35 weekend recap)
   - **Last day of month 21:00** run monthly_summary.py (#36 month-end self-check)
   - **Daily 8:00** run credit_card_reminder.py (remind when card statement/due day approaching, #23)
5. **Configure notification preferences** — ask "shall I use my own channel (Feishu/WeChat) to notify you, or write to alerts.md?"
6. **Save config + write sentinel** — write to `Accounts/agent-config.md` (user-visible, user-editable), **MUST** include `onboarded: true` field. See template below.
7. **Test one transaction** — verify entire flow works

**`Accounts/agent-config.md` template** (Agent auto-generates, user confirms):

```markdown
---
title: Agent Configuration
type: agent-config
onboarded: true
onboarded_at: 2026-06-02
agent_name: Hermes
notification_channel: feishu   # feishu | wechat | alerts-md
vault_path: ~/Obsidian/finance
scheduled_tasks:
  - time: "18:00"
    script: daily_integrity_check.py
    enabled: true
  - time: "20:00"
    script: weekly_summary.py
    weekday: sunday
    enabled: true
  - time: "21:00"
    script: monthly_summary.py
    day: last
    enabled: true
  - time: "08:00"
    script: credit_card_reminder.py
    enabled: true
  - time: "08:05"
    script: installment_check.py
    enabled: true
  - time: "08:10"
    script: loan_payment_reminder.py
    enabled: true
---

# AI Agent Configuration

> This file is auto-generated by the AI Agent during Onboarding; user can edit manually.
> **Important**: `onboarded: true` is the Onboarding completion sentinel. Deleting it = forced re-Onboarding.
> After editing, please tell the Agent so it can re-validate the config integrity.
```

**Why we don't just check `agent-config.md` existence**:
- User may delete the file by accident → sentinel lost → forced re-Onboarding (protective)
- User may corrupt content → missing `onboarded: true` field → forced re-Onboarding
- Only "file exists + onboarded: true + 5 scheduled_tasks all enabled" counts as truly complete

**Why scheduled tasks are needed**:
- Agent is only online when user has a session. Session closed = Agent "sleeps".
- To have Agent proactively remind the user ("payment due today" / "no transactions today"), Agent must be **woken up at a specified time** — only system scheduled tasks can guarantee this.
- Agent's responsibility is to **proactively help the user configure** scheduled tasks + **proactively analyze alerts.md**, not to avoid scheduled tasks.

---

## Execution Flow (AI Agent Standard Steps)

### Step 1: Identify Intent

User input → Determine whether it's **expense / income / transfer**

| Expense Keywords | Income Keywords | Transfer Keywords |
|-----------------|----------------|-------------------|
| 花 (spent), 买 (bought), 付 (pay), 消费 (consume), 支出 (expense), 开支 (spend) | 收 (receive), 到 (arrive), 进 (come in), 赚 (earn), 工资 (salary), 奖金 (bonus), 收入 (income) | 转 (transfer), 转给 (transfer to), 打给 (send to), 调拨 (allocate), 还信用卡 (pay credit card), from X to Y |

> **Important**: When transfer intent is detected, you **must** follow the dual-file pairing workflow (see Step 5-6). Do NOT treat it as expense or income.

### Step 2: Extract Fields

Extract the following fields from user input:

**Expense / Income:**

| Field | Extraction Method | Example |
|-------|------------------|---------|
| `type` | Intent detection | "花了45元" → expense |
| `date` | Time words → YYYY-MM-DD | "今天" → 2026-06-01, "昨天" → 2026-05-31 |
| `amount` | Number extraction | "45元" → 45 |
| `currency` | Currency keywords | "元" → CNY, "刀" → USD, "€" → EUR |
| `account` | Payment tool matching | "支付宝" → Alipay |
| `category` | Keywords → category | See category mapping table below |
| `note` | Original description | User's exact words |
| `status` | Fixed value | ACTIVE |

**Transfer (additional fields):**

| Field | Extraction Method | Example |
|-------|------------------|---------|
| `type` | Transfer intent | "从支付宝转 5000 到招行" → transfer |
| `from_account` | Source account | "支付宝" → Alipay |
| `to_account` | Destination account | "招行" → CMB |
| `transfer_pair_id` | Auto-generated | `T-2026-06-01-abc123` (shared between out and in) |
| `amount` | Number | 5000 |
| `currency` | Currency | CNY |
| `category` | Fixed value | Transfer |

### Step 3: Match Category

Read the category mapping table from `~/Obsidian/finance/Categories/expense-category-rules.md` or `income-category-rules.md`:

**Expense Categories (12 types)**

| Category | Chinese Keywords | English Keywords |
|----------|-----------------|-----------------|
| Food | 午餐、晚餐、外卖、餐厅、沙县 | lunch、dinner、takeout、restaurant |
| Transport | 地铁、公交、打车、滴滴 | subway、bus、taxi、DiDi |
| Shopping | 淘宝、京东、拼多多、超市 | Taobao、JD、Pinduoduo、shopping |
| Entertainment | 电影、游戏、会员、Steam | movie、game、Netflix、Steam |
| Health | 医院、药店、体检 | hospital、pharmacy、checkup |
| Education | 课程、书籍、培训 | course、book、training |
| Housing | 房租、物业、水电 | rent、property、utilities |
| Communication | 话费、宽带、流量 | phone、broadband、data |
| Gift | 红包、礼物、人情 | red envelope、gift、treat |
| Travel | 机票、酒店、旅游 | flight、hotel、travel |
| Investment | 理财、基金、股票 | financial、fund、stock |
| Other | 其他、杂项 | other、misc |

**Income Categories (7 types)**

| Category | Chinese Keywords | English Keywords |
|----------|-----------------|-----------------|
| Salary | 工资、月薪、底薪 | salary、wages |
| Bonus | 年终奖、奖金、绩效 | bonus、year-end |
| Freelance | 兼职、外快、接单 | freelance、side job |
| Investment | 理财利息、投资收益 | investment interest |
| Refund | 退款、退货、补偿 | refund、compensation |
| Gift | 红包、礼金 | red envelope、gift money |
| Other | 其他、偶然收入 | other |

**Transfer Category (1 type):**

| Category | Description |
|----------|-------------|
| Transfer | Money moved between user's own accounts (not income/expense) |

### Step 4: Match Account

Match account name based on payment tool:

| Account | Chinese Keywords | English Keywords |
|---------|-----------------|-----------------|
| Alipay | 支付宝 | Alipay |
| WeChat Pay | 微信、微信支付 | WeChat、WeChat Pay |
| CMB | 招行、招商银行 | CMB、China Merchants Bank |
| ICBC | 工行、工商银行 | ICBC |
| Credit Card | 信用卡 | Credit Card |
| Cash | 现金 | Cash |
| USD Account | 美元账户 | USD Account |

### Step 5: Generate Filename

**Expense / Income:**
```
{date}-{description}-{amount}-{CURRENCY}-ACTIVE.md
```
Example: `2026-06-01-lunch-45-CNY-ACTIVE.md`

**Transfer (dual files):**
```
out: {date}-transfer-out-{from_account}-to-{to_account}-{amount}-{CURRENCY}-ACTIVE.md
in:  {date}-transfer-in-{to_account}-from-{from_account}-{amount}-{CURRENCY}-ACTIVE.md
```
Example:
```
2026-06-01-transfer-out-Alipay-to-CMB-5000-CNY-ACTIVE.md
2026-06-01-transfer-in-CMB-from-Alipay-5000-CNY-ACTIVE.md
```

### Step 6: Create File

**File path (local vault):**
- Expense: `~/Obsidian/finance/Transactions/expenses/{filename}`
- Income: `~/Obsidian/finance/Transactions/incomes/{filename}`
- Transfer-out: `~/Obsidian/finance/Transactions/transfers/out/{filename}`
- Transfer-in: `~/Obsidian/finance/Transactions/transfers/in/{filename}`

**Transfer file frontmatter:**
```yaml
---
type: transfer
date: 2026-06-01
amount: 5000
currency: CNY
category: Transfer
from_account: Alipay
to_account: CMB
transfer_pair_id: T-2026-06-01-abc123   # ⚠️ Must be identical in out and in files
note: "还信用卡前调拨"
tags: [transfer, finance]
status: ACTIVE
created: 2026-06-01
---

**File content format (expense):**
```markdown
---
type: expense
date: 2026-06-01
amount: 45
currency: CNY
category: Food
account: Alipay
payment_method: Alipay
note: "午餐-沙县小吃"
tags: [expense, food]
status: ACTIVE
created: 2026-06-01
---

# 2026-06-01 — Lunch Expense

| Field | Value |
|------|-------|
| **Type** | Expense |
| **Date** | 2026-06-01 |
| **Amount** | 45 CNY |
| **Category** | Food 🍔 |
| **Account** | Alipay |
| **Note** | 午餐-沙县小吃 |
```

### Step 7: Confirm Completion

Tell the user:
- **Expense/Income**: file path + key content
- **Transfer**: 2 file paths + pair ID (critical! user queries pairs by this ID later)
- Can view summary in Dataview dashboard at `~/Obsidian/finance/Dashboards/finance-dashboard.md`

### Step 7.5: Automatic Validation (strongly recommended)

After writing a transaction file, the AI Agent **MUST** call the validation script to ensure project internal consistency:

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/validate_transaction.py <new_file_path>
```

**Validation content**: required fields, valid amount, valid date, valid currency, account registered, **transfer pair complete and fields consistent**.

**Exit codes**:
- `0` = pass, continue silently
- `1` = fail, **soft alert** — file preserved, AI Agent tells user the issue and asks: (a) auto-fix / (b) ignore / (c) delete and re-enter
- `2` = file not found, argument error

**Typical error and dialog**:
> ❌ Validation failed: 2026-06-01-lunch-45-CNY-ACTIVE.md
>   ❌ [ERROR] amount must be > 0 (current: 0)
>
> AI Agent: "This entry failed validation (amount must be positive). Would you like: (a) I'll change it to 45 and re-save / (b) the amount really is 0 (rare, e.g. zero refund) so ignore this alert / (c) delete this entry and re-enter?"

**Why validation is mandatory**: The user only inputs initial balances — all subsequent additions/subtractions are handled by the project. If the project's internal calculation breaks (transfer pair missing, field errors), the balance becomes wrong. The validation script guarantees **the project's own calculation never fails**.

---

## Complete Examples

### Example 1: Expense

**User input:**
> "今天午餐沙县花了45元，支付宝付款"

**AI Agent execution:**
1. type = expense
2. date = 今天 → 2026-06-01
3. amount = 45, currency = CNY
4. account = Alipay
5. Keywords "午餐、沙县" → category = Food
6. note = "午餐-沙县小吃"
7. Create file: `~/Obsidian/finance/Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

### Example 2: Income

**User input:**
> "收到了6月份工资15000元，是招行发的"

**AI Agent execution:**
1. type = income
2. date = 今天 → 2026-06-01
3. amount = 15000, currency = CNY
4. account = CMB
5. Keyword "工资" → category = Salary
6. note = "6月工资"
7. Create file: `~/Obsidian/finance/Transactions/incomes/2026-06-01-salary-15000-CNY-ACTIVE.md`

### Example 3: Multi-currency Expense

**User input:**
> "在亚马逊买了本技术书花了35美元，信用卡支付"

**AI Agent execution:**
1. type = expense
2. date = 今天
3. amount = 35, currency = USD
4. account = Credit Card
5. Keyword "书" → category = Education
6. note = "技术书-亚马逊"
7. Create file: `~/Obsidian/finance/Transactions/expenses/2026-06-01-book-35-USD-ACTIVE.md`

### Example 4: Transfer

**User input:**
> "从支付宝转 5000 到招行，准备还信用卡"

**AI Agent execution:**
1. type = **transfer** (detected "转")
2. date = 今天 → 2026-06-01
3. amount = 5000, currency = CNY
4. from_account = Alipay ("支付宝")
5. to_account = CMB ("招行")
6. Generate pair_id = `T-2026-06-01-abc123`
7. category = Transfer (fixed)
8. Create 2 files:
   - `~/Obsidian/finance/Transactions/transfers/out/2026-06-01-transfer-out-Alipay-to-CMB-5000-CNY-ACTIVE.md`
   - `~/Obsidian/finance/Transactions/transfers/in/2026-06-01-transfer-in-CMB-from-Alipay-5000-CNY-ACTIVE.md`

**Tell the user:**
> Transfer recorded (pair ID: `T-2026-06-01-abc123`)
> - Transfer-out: Alipay → 5000 CNY → `~/Obsidian/finance/Transactions/transfers/out/2026-06-01-transfer-out-Alipay-to-CMB-5000-CNY-ACTIVE.md`
> - Transfer-in: CMB ← 5000 CNY ← `~/Obsidian/finance/Transactions/transfers/in/2026-06-01-transfer-in-CMB-from-Alipay-5000-CNY-ACTIVE.md`
> To find the pair: In Obsidian global search `transfer_pair_id: T-2026-06-01-abc123` to locate both sides at once

---

## Notes

1. **Date format**: Unified `YYYY-MM-DD`, "今天" (today) auto-converts to current date
2. **Amount**: Pure number without symbols (e.g., `45` not `¥45`)
3. **Description**: English or pinyin, connected with `-` (e.g., `lunch`, `subway`, `salary`)
4. **Status**: New files always `status: ACTIVE`
5. **Multi-currency**: Record as user describes, no conversion
6. **Keyword matching**: Precise keywords first (e.g., "沙县" → Food), then broader (e.g., "其他" → Other)
7. **Default account**: If user doesn't specify, default to Alipay (expense) or CMB (income)
8. **File location**: Unified under `~/Obsidian/finance/Transactions/`
9. **Transfer detection**: When trigger words like "transfer / send / allocate / pay credit card / from X to Y" are detected, you **must** follow the dual-file pairing workflow — do NOT treat as expense or income
10. **Pair ID consistency**: The `transfer_pair_id` in the out and in files **must be identical**, otherwise pair lookup will fail
11. **Pair ID uniqueness**: Use a fresh `T-{date}-{random-string}` for every transfer, to avoid clashes with historical data

---

## Local File Path Quick Reference

| File | Path |
|------|------|
| AI Agent Workflow | `~/Project/obsidian-personal-finance-tracker/zh/AGENTS.md` |
| Category/Account Mapping | `~/Project/obsidian-personal-finance-tracker/zh/QUICK-REFERENCE.md` |
| Expense Category Rules | `~/Obsidian/finance/Categories/expense-category-rules.md` |
| Income Category Rules | `~/Obsidian/finance/Categories/income-category-rules.md` |
| Transfer Categories | `~/Obsidian/finance/Categories/transfer-categories.md` |
| Dashboard | `~/Obsidian/finance/Dashboards/finance-dashboard.md` |
| Account List | `~/Obsidian/finance/Accounts/account-list.md` |
| Expense Template | `~/Obsidian/finance/Templates/expense-template.md` |
| Income Template | `~/Obsidian/finance/Templates/income-template.md` |
| Transfer Template | `~/Obsidian/finance/Templates/transfer-template.md` |
| **Ledger Data** | `~/Obsidian/finance/Transactions/{expenses,incomes,transfers/{out,in}}/` |

---

## Validation Scripts (scripts/) — Tools for the Agent, Not Standalone Services

The project ships with zero-dependency Python validation scripts (Python 3.8+ standard library only). Works for all users, all platforms, all AI Agents.

**Core positioning shift**: scripts do **NOT** auto-run, do **NOT** depend on system cron, do **NOT** send webhooks — **all of that is the Agent's responsibility**.

### scripts/validate_transaction.py — Single Transaction Validation

**When**: AI Agent calls **immediately** after writing a transaction file (Step 7.5). **This is the Agent's job, not the user's**.

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/validate_transaction.py <new_file_path>
```

Validates: required fields, amount > 0, valid date, valid currency, account registered, **transfer pair complete and consistent**.

### scripts/daily_integrity_check.py — Daily Conservation

**When**: **Agent itself decides** at session start "is it time to run?", and runs if so. No system cron dependency.

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py
```

Validates:
1. All transfer out and in files are paired (no orphans)
2. Paired files have identical amount, currency, from_account, to_account
3. Per-currency transfer_in == transfer_out (self-consistent)
4. Python balance calculation vs accumulation verification (Path A vs Path B self-consistent — this is the core guarantee)
5. Account overdraft check (soft alert)

### scripts/weekly_dashboard_check.py — Weekly Structure Check

**When**: Agent proactively runs Sunday at 8 AM.

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/weekly_dashboard_check.py
```

Validates: dashboard files reference all required fields, account table complete, prints authoritative balances for user cross-check against Dataview display.

### scripts/credit_card_reminder.py — Credit Card Payment Reminder (#23)

**When**: Agent helps user configure daily 8:00 scheduled task.

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/credit_card_reminder.py --vault ~/Obsidian/finance
```

Validates:
- Scans `Accounts/account-list.md` for `type: credit` accounts
- Computes next statement date + due date for each card (handles month-crossing, month-end edge cases)
- Due date ≤ 5 days → WARN, already past → ERROR
- Writes to `alerts.md`

**Prerequisite**: credit card accounts must have `statement_day` + `payment_due_day` fields in `account-list.md`, otherwise INFO prompts user to fill (soft alert, non-blocking).

### scripts/installment_check.py — Installment Integrity Check (#24)

**When**: Agent helps user configure daily 8:05 scheduled task.

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/installment_check.py --vault ~/Obsidian/finance
```

Validates:
- Groups all installment expenses by `installment_group_id`
- Validates ① total count ② field consistency (amount/currency/account/category) ③ PENDING due date ④ orphan installments (1 item but marked as installment)
- Writes to `alerts.md`

### scripts/loan_payment_reminder.py — Loan Payment Reminder (#37)

**When**: Agent helps user configure daily 8:10 scheduled task (5 min after installment check).

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/loan_payment_reminder.py --vault ~/Obsidian/finance
```

**Trigger condition**: Detects `type: loan` accounts in `Accounts/account-list.md`.

**Validation**:
- Loan account required field check (Principal / Monthly Payment / Remaining Months / Start Month); missing fields → INFO
- Next payment date: last day of start month, then same day each subsequent month (auto-handles 2-day count)
- **≤5 days**: WARN ("Payment approaching, amount X")
- **Overdue ≤3 days, not recorded**: ERROR ("Payment X days overdue, not yet recorded!")
- **Overdue 4+ days, not recorded**: ERROR ("Severely overdue")
- **Current month paid**: INFO ("Paid, next payment...")

**Supports 4 loan fields** (zh + en): `贷款总额/Principal` / `月供/Monthly Payment` / `剩余期数/Remaining Months` / `起始月/Start Month`

**Companion**: `monthly_summary.py` auto-adds "💳 Loan account progress" section to monthly reports (principal / paid / percentage / remaining months)

---

### scripts/installment_helper.py — Installment Template Generator (#24)

**When**: After user writes the first installment expense, Agent **calls immediately**.

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/installment_helper.py create \
  --first-file ~/Obsidian/finance/Transactions/expenses/<first_installment_file> \
  --total 12
```

What it does:
- Reads first installment frontmatter, copies amount/currency/account/category/note
- Auto-generates N-1 PENDING expense templates (dates incremented)
- If `installment_group_id` is missing, auto-generates `INS-{date}-{account}-{amount}` format
- User flips status=PENDING → ACTIVE on actual deduction, then runs `validate_transaction.py`

### scripts/weekly_summary.py — Weekend Recap (#35)

**When**: Agent helps user configure Sunday 20:00 weekly scheduled task.

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/weekly_summary.py --vault ~/Obsidian/finance
```

Validates:
- Range: this Monday 00:00 ~ this Sunday 23:59
- Output: tx count / total expense / total income / top 3 categories / account balance changes / week-over-week
- Writes to `alerts.md`

**Agent follow-up**: reads `alerts.md`, pushes "23 transactions this week, food ¥820 (-32%)" via own channel.

### scripts/monthly_summary.py — Month-end Self-Check (#36)

**When**: Agent helps user configure last-day-of-month 21:00 scheduled task.

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/monthly_summary.py --vault ~/Obsidian/finance
# Historical month
python3 ~/Project/obsidian-personal-finance-tracker/scripts/monthly_summary.py --vault ~/Obsidian/finance --month 2026-03
```

Validates:
- Range: 1st of month ~ last day of month (cuts off at today if not yet ended)
- Output: tx count / expense / income / savings rate / category breakdown / cross-account flow
- Writes to `alerts.md`

**Savings rate formula**: `(income − expense) / income` (transfers out don't count as expense, transfer_in/out counts as cross-account flow).

### Notification Methods (scripts do the basics, Agent does the rest)

The scripts do **only** two things (no configuration needed):

1. **`~/Obsidian/finance/Dashboards/alerts.md`** — always written, user views in Obsidian
2. **Desktop notification** — macOS `osascript` / Linux `notify-send`, popup alert

**All other notifications (Feishu / WeChat / email / SMS) are the Agent's job** — the Agent reads alerts.md and uses its own existing messaging channel to push to the user. **Do NOT** ask the user to configure webhooks, get Bark keys, or sign up for Server酱 — that's the Agent's job, not the user's.

For detailed proactive behavior rules see [AGENTS-PROACTIVE.md](../../en/AGENTS-PROACTIVE.md).

---

## First-Time Installation

If installing from GitHub for the first time, follow these steps:

```bash
# 1. Clone project to local
git clone https://github.com/lovepigpanda/obsidian-personal-finance-tracker.git ~/Project/obsidian-personal-finance-tracker

# 2. Create finance directory in Obsidian vault
mkdir -p ~/Obsidian/finance/{Templates,Categories,Dashboards,Accounts,Transactions/{expenses,incomes,transfers/{out,in}}}

# 3. Copy templates and rule files to vault
cp ~/Project/obsidian-personal-finance-tracker/zh/Templates/*.md ~/Obsidian/finance/Templates/
cp ~/Project/obsidian-personal-finance-tracker/zh/Categories/*.md ~/Obsidian/finance/Categories/
cp ~/Project/obsidian-personal-finance-tracker/zh/Dashboards/*.md ~/Obsidian/finance/Dashboards/
cp ~/Project/obsidian-personal-finance-tracker/zh/Accounts/*.md ~/Obsidian/finance/Accounts/

# 4. Install skill to each AI Agent
aweskill install https://github.com/lovepigpanda/obsidian-personal-finance-tracker
aweskill agent add --agent openclaw skill obsidian-finance-track
aweskill agent add --agent claude-code skill obsidian-finance-track
```

> Note: Do NOT copy `Transactions/` directory from GitHub — it's your private ledger.

---

> Skill: obsidian-finance-track | Version: V1.0 | For AI Agent use
> Project: https://github.com/lovepigpanda/obsidian-personal-finance-tracker
