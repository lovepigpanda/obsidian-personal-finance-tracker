---
name: obsidian-finance-track
tagline: 你的 AI 理财搭档 · Your AI Finance Partner
description: >
  Obsidian Personal Finance Tracking AI Agent Skill. Load this skill when the user describes
  accounting-related content (expenses, income, transfers, wallet balance, salary, shopping, etc.)
  or explicitly uses trigger words like "记账" (record), "记一笔" (log one), "花了多少" (how much spent),
  "收到" (received), etc.

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
  - expense
  - income
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
                                      │   └── incomes/          ← One .md file per income
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
│   └── income-template.md         ← Income record template
├── Categories/                    ← Category rules (read by AI Agent)
│   ├── expense-categories.md      ← Expense category descriptions
│   ├── expense-category-rules.md  ← Expense keyword mappings
│   ├── income-categories.md       ← Income category descriptions
│   └── income-category-rules.md  ← Income keyword mappings
├── Dashboards/                    ← Dataview dashboards
│   └── finance-dashboard.md       ← Main dashboard
├── Accounts/                      ← Account list
│   └── account-list.md            ← Account names + initial balances
└── Transactions/                  ← ⭐ Actual ledger data (local, private)
    ├── expenses/                  ← One .md file per expense
    │   └── YYYY-MM-DD-*-ACTIVE.md
    └── incomes/                   ← One .md file per income
        └── YYYY-MM-DD-*-ACTIVE.md
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
Write to ~/Obsidian/finance/Transactions/{expenses,incomes}/
       ↓
Dataview dashboard (~/Obsidian/finance/Dashboards/finance-dashboard.md) auto-updates
```

---

## Trigger Conditions

Load this skill when ANY of the following conditions are met:

1. **Explicit triggers**: 记账 (record), 记一笔 (log one), 花 (spent), 买 (bought), 支出 (expense), 收入 (income), 收到 (received), 工资 (salary), 消费 (consume)
2. **Financial keywords**: 支付宝 (Alipay), 微信支付 (WeChat Pay), 银行卡 (bank card), 报销 (reimbursement), 退款 (refund), 红包 (red envelope), 余额 (balance)
3. **English keywords**: expense, income, spent, paid, received, salary, budget
4. **Intent detection**: User describes money flowing in or out (regardless of wording)

---

## Execution Flow (AI Agent Standard Steps)

### Step 1: Identify Intent

User input → Determine whether it's an **expense** or **income**

| Expense Keywords | Income Keywords |
|-----------------|----------------|
| 花 (flower/spent), 买 (buy), 付 (pay), 消费 (consume), 支出 (expense), 开支 (spend) | 收 (receive), 到 (arrive), 进 (come in), 赚 (earn), 工资 (salary), 奖金 (bonus), 收入 (income) |

### Step 2: Extract Fields

Extract the following fields from user input:

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

```
{date}-{description}-{amount}-{CURRENCY}-ACTIVE.md
```

Example: `2026-06-01-lunch-45-CNY-ACTIVE.md`

### Step 6: Create File

**File path (local vault):**
- Expense: `~/Obsidian/finance/Transactions/expenses/{filename}`
- Income: `~/Obsidian/finance/Transactions/incomes/{filename}`

**File content format:**
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
- File path: `~/Obsidian/finance/Transactions/expenses/{filename}`
- Key content (type, amount, category, account)
- Can view summary in Dataview dashboard at `~/Obsidian/finance/Dashboards/finance-dashboard.md`

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

---

## Local File Path Quick Reference

| File | Path |
|------|------|
| AI Agent Workflow | `~/Project/obsidian-personal-finance-tracker/zh/AGENTS.md` |
| Category/Account Mapping | `~/Project/obsidian-personal-finance-tracker/zh/QUICK-REFERENCE.md` |
| Expense Category Rules | `~/Obsidian/finance/Categories/expense-category-rules.md` |
| Income Category Rules | `~/Obsidian/finance/Categories/income-category-rules.md` |
| Dashboard | `~/Obsidian/finance/Dashboards/finance-dashboard.md` |
| Account List | `~/Obsidian/finance/Accounts/account-list.md` |
| Expense Template | `~/Obsidian/finance/Templates/expense-template.md` |
| Income Template | `~/Obsidian/finance/Templates/income-template.md` |
| **Ledger Data** | `~/Obsidian/finance/Transactions/{expenses,incomes}/` |

---

## First-Time Installation

If installing from GitHub for the first time, follow these steps:

```bash
# 1. Clone project to local
git clone https://github.com/lovepigpanda/obsidian-personal-finance-tracker.git ~/Project/obsidian-personal-finance-tracker

# 2. Create finance directory in Obsidian vault
mkdir -p ~/Obsidian/finance/{Templates,Categories,Dashboards,Accounts,Transactions/{expenses,incomes}}

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