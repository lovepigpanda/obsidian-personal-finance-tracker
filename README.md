# Obsidian Personal Finance Tracker

> 简体中文 | [English](#english)

---

## ✨ 功能特点

- ✅ **支出记录** — 金额/分类/账户/支付方式/备注
- ✅ **收入记录** — 金额/来源分类/账户/备注
- ✅ **多账户余额追踪** — 自动计算（初始余额 + 收入 - 支出）
- ✅ **多币种分别统计** — CNY/USD/EUR 分开显示，不折算
- ✅ **分类自动映射** — 输入关键词自动 suggest 分类
- ✅ **月度汇总报告** — Dataview 自动生成
- ✅ **主仪表盘** — 本月余额/分类占比/趋势
- 🤖 **AI Agent 支持** — 自然语言记账，自动创建交易文件（见 `AGENTS.md`）
- 📅 **多币种汇率换算**（v1.1）
- 🏦 **银行 API 自动同步**（v2.0）

---

## 🤖 AI Agent 使用

本系统主要面向 **AI Agent**（Claude/Hermes 等），用户用自然语言描述交易，AI Agent 自动：

1. 解析意图（支出/收入）、日期、金额、币种
2. 匹配账户和分类（根据 `QUICK-REFERENCE.md` 映射表）
3. 在 `Transactions/` 目录下创建对应 `.md` 文件

**示例：**

用户 → `"午餐沙县花了45元，支付宝付款"`

AI Agent → 自动创建 `Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

详见：[AGENTS.md](zh/AGENTS.md) · [QUICK-REFERENCE.md](zh/QUICK-REFERENCE.md)

---

## 📁 项目结构

```
obsidian-personal-finance-tracker/
├── README.md                       # 双语入口
├── LICENSE                        # MIT
├── SPEC.md                        # 项目规格
├── zh/                            # 🌏 中文版（主要）
│   ├── AGENTS.md                  # 🤖 AI Agent 使用指南
│   ├── QUICK-REFERENCE.md         # 📋 AI Agent 快速参考
│   ├── Templates/                 # Templater 模板
│   ├── Transactions/              # 交易文件
│   ├── Dashboards/               # Dataview 仪表盘
│   ├── Accounts/                 # 账户列表
│   └── Categories/               # 分类规则
└── en/                            # 🌎 English version
    ├── AGENTS.md                 # 🤖 AI Agent guide
    ├── QUICK-REFERENCE.md        # 📋 AI Agent quick reference
    ├── Templates/
    ├── Transactions/
    ├── Dashboards/
    ├── Accounts/
    └── Categories/
```

---

## 🚀 快速开始

### AI Agent 接入（推荐）

1. 克隆本仓库到本地（或将 `zh/` 复制到 Obsidian vault）
2. AI Agent 读取 `zh/AGENTS.md` 了解工作流程
3. AI Agent 参考 `zh/QUICK-REFERENCE.md` 快速查找分类/账户映射
4. 用户用自然语言描述交易，AI Agent 自动创建文件

### 人类手动录入

1. 在 Obsidian 中安装 **Dataview** 和 **Templater** 插件
2. 复制 `zh/Templates/`、`zh/Dashboards/`、`zh/Accounts/`、`zh/Categories/` 到 vault
3. Templater → 新建笔记 → 选择 `expense-template.md` 或 `income-template.md`
4. 打开 `zh/Dashboards/finance-dashboard.md` 查看财务概况

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
2. 账户余额由 Dataview 实时计算，初始余额需在 `zh/Accounts/account-list.md` 中手动设置
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

> English | [简体中文](#简体中文)

---

## ✨ Features

- ✅ **Expense tracking** — amount / category / account / payment method / note
- ✅ **Income tracking** — amount / source category / account / note
- ✅ **Multi-account balance tracking** — auto-calculated (initial balance + income − expenses)
- ✅ **Multi-currency separate display** — CNY / USD / EUR shown separately, no conversion
- ✅ **Automatic category mapping** — keyword input auto-suggests categories
- ✅ **Monthly summary reports** — auto-generated via Dataview
- ✅ **Main dashboard** — monthly balance / category breakdown / trends
- 🤖 **AI Agent support** — natural language accounting, auto-creates transaction files (see `AGENTS.md`)
- 📅 **Multi-currency exchange rates** (v1.1)
- 🏦 **Bank API auto-sync** (v2.0)

---

## 🤖 AI Agent Usage

This system is primarily designed for **AI Agents** (Claude / Hermes / etc.). The user describes a transaction in natural language, and the AI Agent automatically:

1. Parses intent (expense/income), date, amount, currency
2. Matches account and category (using `QUICK-REFERENCE.md` mapping tables)
3. Creates the corresponding `.md` file under `Transactions/`

**Example:**

User → `"Lunch at Shaxian spent 45 CNY, paid via Alipay"`

AI Agent → Auto-creates `Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

See: [AGENTS.md](en/AGENTS.md) · [QUICK-REFERENCE.md](en/QUICK-REFERENCE.md)

---

## 📁 Project Structure

```
obsidian-personal-finance-tracker/
├── README.md                       # Bilingual entry point
├── LICENSE                        # MIT
├── SPEC.md                        # Project specification
├── zh/                            # 🌏 Chinese version (primary)
│   ├── AGENTS.md                  # 🤖 AI Agent guide
│   ├── QUICK-REFERENCE.md         # 📋 AI Agent quick reference
│   ├── Templates/                 # Templater templates
│   ├── Transactions/              # Transaction files
│   ├── Dashboards/               # Dataview dashboards
│   ├── Accounts/                 # Account list
│   └── Categories/               # Category rules
└── en/                            # 🌎 English version
    ├── AGENTS.md                 # 🤖 AI Agent guide
    ├── QUICK-REFERENCE.md        # 📋 AI Agent quick reference
    ├── Templates/
    ├── Transactions/
    ├── Dashboards/
    ├── Accounts/
    └── Categories/
```

---

## 🚀 Quick Start

### AI Agent Integration (Recommended)

1. Clone this repo to local (or copy `en/` folder to your Obsidian vault)
2. AI Agent reads `en/AGENTS.md` for workflow
3. AI Agent references `en/QUICK-REFERENCE.md` for category/account lookups
4. User describes transactions in natural language, AI Agent creates files

### Manual Human Entry

1. Install **Dataview** and **Templater** plugins in Obsidian
2. Copy `en/Templates/`, `en/Dashboards/`, `en/Accounts/`, `en/Categories/` to your vault
3. Templater → New Note → select `expense-template.md` or `income-template.md`
4. Open `en/Dashboards/finance-dashboard.md` to view financial overview

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
2. Account balances are calculated in real-time by Dataview; initial balances must be set in `en/Accounts/account-list.md`
3. China bank APIs not yet supported; auto-sync deferred (v2.0)

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

## 📄 License

MIT License