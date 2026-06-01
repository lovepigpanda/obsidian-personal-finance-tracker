# Obsidian Personal Finance Tracker

### 🤖 你的 AI 理财搭档 · Your AI Finance Partner

---

## ⚠️ 数据存储架构 — 重要

**技能代码与账本数据完全分离：**

| 内容 | 位置 | 说明 |
|------|------|------|
| 🤖 **AI Agent 技能** | GitHub 仓库 `skills/obsidian-finance-track/` | `git pull` 同步更新 |
| 📋 **模板/规则/仪表盘** | GitHub 仓库 `zh/` | `git pull` 同步更新 |
| 💰 **你的账本数据** | `~/Obsidian/finance/Transactions/` | **本地私有，永不上传** |

```
GitHub 仓库（技能代码，可分发）
├── skills/obsidian-finance-track/   ← AI Agent 技能
├── zh/                               ← 模板、规则、文档
└── .gitignore                        ← 忽略 Transactions/

本地 Obsidian vault（账本数据，私有）
└── ~/Obsidian/finance/
    ├── Templates/                    ← 模板（可从 GitHub 复制）
    ├── Categories/                   ← 分类规则（可从 GitHub 复制）
    ├── Dashboards/                   ← 仪表盘（可从 GitHub 复制）
    ├── Accounts/                    ← 账户列表
    └── Transactions/               ← 💰 你的真实账本数据（不上传）
```

**为什么这样设计？**
- GitHub 项目是"技能"，别人可以放心地用 `git pull` 更新，不必担心覆盖账本
- 你的账本数据永远在本地，不会上传到 GitHub
- 模板和规则可以从 GitHub 同步，但每笔交易记录绝对安全

---

## ✨ 功能特点

- ✅ **支出记录** — 金额/分类/账户/支付方式/备注
- ✅ **收入记录** — 金额/来源分类/账户/备注
- ✅ **多账户余额追踪** — 自动计算（初始余额 + 收入 - 支出）
- ✅ **多币种分别统计** — CNY/USD/EUR 分开显示，不折算
- ✅ **分类自动映射** — 输入关键词自动 suggest 分类
- ✅ **月度汇总报告** — Dataview 自动生成
- ✅ **主仪表盘** — 本月余额/分类占比/趋势
- 🤖 **AI Agent 支持** — 自然语言记账，自动创建交易文件
- 📅 **多币种汇率换算**（v1.1）
- 🏦 **银行 API 自动同步**（v2.0）

---

## 🤖 AI Agent 使用

本系统主要面向 **AI Agent**（Claude/Hermes/OpenClaw 等），用户用自然语言描述交易，AI Agent 自动：

1. 解析意图（支出/收入）、日期、金额、币种
2. 匹配账户和分类（根据 `QUICK-REFERENCE.md` 映射表）
3. 在 `~/Obsidian/finance/Transactions/` 下创建对应 `.md` 文件

**示例：**

用户 → `"午餐沙县花了45元，支付宝付款"`

AI Agent → 自动创建 `~/Obsidian/finance/Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

详见：[AGENTS.md](zh/AGENTS.md) · [QUICK-REFERENCE.md](zh/QUICK-REFERENCE.md)

---

## 📁 项目结构

```
obsidian-personal-finance-tracker/     ← GitHub 仓库（技能代码）
├── skills/obsidian-finance-track/    ← 🤖 AI Agent 技能（中文+英文）
├── zh/                                # 🌏 中文版
│   ├── AGENTS.md                      # AI Agent 使用指南
│   ├── QUICK-REFERENCE.md            # 快速参考
│   ├── Templates/                    # 模板文件
│   ├── Dashboards/                   # Dataview 仪表盘
│   ├── Accounts/                     # 账户列表
│   └── Categories/                  # 分类规则
├── en/                                # 🌎 English version
└── .gitignore                        # 忽略 Transactions/ 目录
```

---

## 🚀 快速开始

### AI Agent 接入（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/lovepigpanda/obsidian-personal-finance-tracker.git ~/Project/obsidian-personal-finance-tracker

# 2. 在 Obsidian vault 创建账本目录
mkdir -p ~/Obsidian/finance/{Templates,Categories,Dashboards,Accounts,Transactions/{expenses,incomes}}

# 3. 复制模板和规则（从 GitHub 到本地 vault）
cp ~/Project/obsidian-personal-finance-tracker/zh/Templates/*.md ~/Obsidian/finance/Templates/
cp ~/Project/obsidian-personal-finance-tracker/zh/Categories/*.md ~/Obsidian/finance/Categories/
cp ~/Project/obsidian-personal-finance-tracker/zh/Dashboards/*.md ~/Obsidian/finance/Dashboards/
cp ~/Project/obsidian-personal-finance-tracker/zh/Accounts/*.md ~/Obsidian/finance/Accounts/

# 4. 安装 AI Agent 技能
aweskill install https://github.com/lovepigpanda/obsidian-personal-finance-tracker
aweskill agent add --agent openclaw skill obsidian-finance-track
aweskill agent add --agent claude-code skill obsidian-finance-track
```

### 人类手动录入

1. 在 Obsidian 中安装 **Dataview** 和 **Templater** 插件
2. 复制 `zh/Templates/`、`zh/Dashboards/`、`zh/Accounts/`、`zh/Categories/` 到 `~/Obsidian/finance/`
3. Templater → 新建笔记 → 选择 `expense-template.md` 或 `income-template.md`
4. 打开 `~/Obsidian/finance/Dashboards/finance-dashboard.md` 查看财务概况

---

## 🛠️ 插件依赖

| 插件 | 必须 | 说明 |
|------|------|------|
| Dataview | ✅ | 查询和渲染仪表盘 |
| Templater | ✅ | 交互式录入模板（人类使用） |
| Commander | ❌ | 快捷命令（可选） |
| Obsidian Charts | ❌ | 趋势图展示（可选） |

---

## ⚠️ 已知限制

1. 多币种汇率需要手动维护（v1.1 计划自动获取）
2. 账户余额由 Dataview 实时计算，初始余额需在 `Accounts/account-list.md` 中手动设置
3. 国内银行 API 暂不支持，自动同步功能延后（v2.0）

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT License

---

***

<a name="english"></a>

# Obsidian Personal Finance Tracker

### 🤖 你的 AI 理财搭档 · Your AI Finance Partner

> [简体中文](#简体中文) | English

---

## ⚠️ Data Storage Architecture — Important

**Skill code and ledger data are completely separated:**

| Content | Location | Notes |
|---------|----------|-------|
| 🤖 **AI Agent skill** | GitHub repo `skills/obsidian-finance-track/` | `git pull` to update |
| 📋 **Templates/rules/dashboards** | GitHub repo `zh/` | `git pull` to update |
| 💰 **Your ledger data** | `~/Obsidian/finance/Transactions/` | **Local only, never upload** |

```
GitHub repo (skill code, shareable)
├── skills/obsidian-finance-track/   ← AI Agent skill
├── zh/                              ← Templates, rules, docs
└── .gitignore                       ← Ignores Transactions/

Local Obsidian vault (ledger data, private)
└── ~/Obsidian/finance/
    ├── Templates/                    ← Templates (copy from GitHub)
    ├── Categories/                   ← Category rules (copy from GitHub)
    ├── Dashboards/                   ← Dashboards (copy from GitHub)
    ├── Accounts/                     ← Account list
    └── Transactions/                ← 💰 Your real ledger data (never upload)
```

**Why this design?**
- GitHub repo is the "skill" — others can safely `git pull` to update without touching their ledger
- Your ledger data stays local, never uploaded to GitHub
- Templates and rules sync from GitHub, but every transaction record is safe

---

## ✨ Features

- ✅ **Expense tracking** — amount / category / account / payment method / note
- ✅ **Income tracking** — amount / source category / account / note
- ✅ **Multi-account balance tracking** — auto-calculated (initial balance + income − expenses)
- ✅ **Multi-currency separate display** — CNY / USD / EUR shown separately, no conversion
- ✅ **Automatic category mapping** — keyword input auto-suggests categories
- ✅ **Monthly summary reports** — auto-generated via Dataview
- ✅ **Main dashboard** — monthly balance / category breakdown / trends
- 🤖 **AI Agent support** — natural language accounting, auto-creates transaction files
- 📅 **Multi-currency exchange rates** (v1.1)
- 🏦 **Bank API auto-sync** (v2.0)

---

## 🤖 AI Agent Usage

This system is designed for **AI Agents** (Claude / Hermes / OpenClaw / etc.). The user describes a transaction in natural language, and the AI Agent automatically:

1. Parses intent (expense/income), date, amount, currency
2. Matches account and category (using `QUICK-REFERENCE.md` mapping tables)
3. Creates the corresponding `.md` file under `~/Obsidian/finance/Transactions/`

**Example:**

User → `"Lunch at Shaxian spent 45 CNY, paid via Alipay"`

AI Agent → Auto-creates `~/Obsidian/finance/Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

See: [AGENTS.md](en/AGENTS.md) · [QUICK-REFERENCE.md](en/QUICK-REFERENCE.md)

---

## 📁 Project Structure

```
obsidian-personal-finance-tracker/     ← GitHub repo (skill code)
├── skills/obsidian-finance-track/    ← 🤖 AI Agent skill (zh + en)
├── zh/                                # 🌏 Chinese version
│   ├── AGENTS.md                     # AI Agent guide
│   ├── QUICK-REFERENCE.md            # Quick reference
│   ├── Templates/                    # Template files
│   ├── Dashboards/                   # Dataview dashboards
│   ├── Accounts/                     # Account list
│   └── Categories/                  # Category rules
├── en/                                # 🌎 English version
└── .gitignore                        # Ignores Transactions/
```

---

## 🚀 Quick Start

### AI Agent Integration (Recommended)

```bash
# 1. Clone the project
git clone https://github.com/lovepigpanda/obsidian-personal-finance-tracker.git ~/Project/obsidian-personal-finance-tracker

# 2. Create ledger directory in Obsidian vault
mkdir -p ~/Obsidian/finance/{Templates,Categories,Dashboards,Accounts,Transactions/{expenses,incomes}}

# 3. Copy templates and rules (from GitHub to local vault)
cp ~/Project/obsidian-personal-finance-tracker/zh/Templates/*.md ~/Obsidian/finance/Templates/
cp ~/Project/obsidian-personal-finance-tracker/zh/Categories/*.md ~/Obsidian/finance/Categories/
cp ~/Project/obsidian-personal-finance-tracker/zh/Dashboards/*.md ~/Obsidian/finance/Dashboards/
cp ~/Project/obsidian-personal-finance-tracker/zh/Accounts/*.md ~/Obsidian/finance/Accounts/

# 4. Install AI Agent skill
aweskill install https://github.com/lovepigpanda/obsidian-personal-finance-tracker
aweskill agent add --agent openclaw skill obsidian-finance-track
aweskill agent add --agent claude-code skill obsidian-finance-track
```

### Manual Human Entry

1. Install **Dataview** and **Templater** plugins in Obsidian
2. Copy `zh/Templates/`, `zh/Dashboards/`, `zh/Accounts/`, `zh/Categories/` to `~/Obsidian/finance/`
3. Templater → New Note → select `expense-template.md` or `income-template.md`
4. Open `~/Obsidian/finance/Dashboards/finance-dashboard.md` to view financial overview

---

## 🛠️ Plugin Dependencies

| Plugin | Required | Note |
|--------|----------|------|
| Dataview | ✅ | Query & render dashboards |
| Templater | ✅ | Interactive entry templates (human use) |
| Commander | ❌ | Quick commands (optional) |
| Obsidian Charts | ❌ | Trend charts (optional) |

---

## ⚠️ Known Limitations

1. Multi-currency exchange rates require manual maintenance (v1.1 plans auto-fetch)
2. Account balances are calculated in real-time by Dataview; initial balances must be set in `Accounts/account-list.md`
3. China bank APIs not yet supported; auto-sync deferred (v2.0)

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

## 📄 License

MIT License