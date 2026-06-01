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
triggers:
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
version: V1.0
status: ACTIVE
tags: [finance, obsidian, accounting, agent, nlp]
author: lovepigpanda
github: https://github.com/lovepigpanda/obsidian-personal-finance-tracker
---

# Obsidian Finance Track — AI Agent Accounting Skill

> This skill enables the AI Agent to perform natural language accounting: parse user input →
> match categories/accounts → create transaction .md files → update dashboard

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

## Validation Scripts (scripts/)

The project ships with zero-dependency Python validation scripts (Python 3.8+ standard library only). Works for all users, all platforms, all AI Agents.

### scripts/validate_transaction.py — Single Transaction Validation

**When**: AI Agent calls immediately after writing a transaction file (Step 7.5).

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/validate_transaction.py <new_file_path>
```

Validates: required fields, amount > 0, valid date, valid currency, account registered, **transfer pair complete and consistent**.

### scripts/daily_integrity_check.py — Daily Conservation

**When**: Run on a schedule daily (cron / launchd / GitHub Actions), independent of AI Agent.

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py
```

Validates:
1. All transfer out and in files are paired (no orphans)
2. Paired files have identical amount, currency, from_account, to_account
3. Per-currency transfer_in == transfer_out (self-consistent)
4. Python balance calculation vs accumulation verification (Path A vs Path B self-consistent — this is the core guarantee)
5. Account overdraft check (soft alert)

On failure: **automatically** writes to `~/Obsidian/finance/Dashboards/alerts.md`, sends desktop notification, optional webhook push.

### scripts/weekly_dashboard_check.py — Weekly Structure Check

```bash
python3 ~/Project/obsidian-personal-finance-tracker/scripts/weekly_dashboard_check.py
```

Validates: dashboard file references all required fields, account table complete, prints authoritative balances for user to cross-check Dataview display.

### Cron Configuration (recommended for all users)

**macOS launchd** (user-level):
```bash
# Write ~/Library/LaunchAgents/com.local.obsidian-finance-daily.plist
# WatchPaths monitor ~/Obsidian/finance/Transactions/ for new files
# Program triggers validate_transaction.py
```

**Linux/macOS crontab**:
```cron
# Daily at 6 AM run conservation check
0 6 * * * /usr/bin/python3 ~/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py
```

**GitHub Actions** (for users syncing vault to GitHub): see `.github/workflows/finance-check.yml` (project-included)

> **Key design**: single-transaction validation is called by AI Agent (covers 80%), system cron is the safety net (covers 100% — including user manually entering via Templater).

### Notification Methods (auto-enabled)

All validation failures are automatically reported via:

1. **`~/Obsidian/finance/Dashboards/alerts.md`** — always written, user views in Obsidian
2. **Desktop notification** — macOS `osascript` / Linux `notify-send`, popup alert
3. **Webhook push (optional)** — set environment variables to enable:
   - `BARK_KEY` → Bark (iOS)
   - `PUSHPLUS_TOKEN` → PushPlus (WeChat)
   - `SCT_KEY` → Server酱 (WeChat)
   - `OBSIDIAN_FINANCE_WEBHOOK_URL` → generic webhook

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
