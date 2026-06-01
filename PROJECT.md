# obsidian-personal-finance-tracker — Project Index

> Multi-language personal finance tracking system for Obsidian + AI Agent

---

## 🌏 Language Versions

| Version | Path | Description |
|---------|------|-------------|
| 🌏 Chinese (Primary) | `zh/` | 中文版（主要版本） |
| 🌎 English | `en/` | English version |

---

## 📁 Directory Structure

```
obsidian-personal-finance-tracker/
├── README.md                       # Bilingual entry point
├── LICENSE                         # MIT License
├── SPEC.md                         # Project specification
├── zh/                             # 🌏 Chinese version
│   ├── AGENTS.md                   # 🤖 AI Agent guide
│   ├── QUICK-REFERENCE.md          # 📋 AI Agent quick reference
│   ├── Templates/
│   │   ├── expense-template.md     # Templater 支出模板
│   │   └── income-template.md      # Templater 收入模板
│   ├── Transactions/
│   │   ├── expenses/               # 支出文件
│   │   └── incomes/               # 收入文件
│   ├── Dashboards/
│   │   └── finance-dashboard.md    # 主仪表盘
│   ├── Accounts/
│   │   └── account-list.md         # 账户列表
│   └── Categories/
│       ├── expense-categories.md   # 支出分类定义
│       ├── expense-category-rules.md  # 支出分类规则
│       ├── income-categories.md     # 收入分类定义
│       └── income-category-rules.md   # 收入分类规则
├── en/                             # 🌎 English version
│   ├── AGENTS.md                   # 🤖 AI Agent guide
│   ├── QUICK-REFERENCE.md          # 📋 AI Agent quick reference
│   ├── Templates/
│   │   ├── expense-template.md
│   │   └── income-template.md
│   ├── Transactions/
│   ├── Dashboards/
│   ├── Accounts/
│   └── Categories/
└── Scripts/
```

---

## 🎯 Use Case

**AI Agent Natural Language Finance Tracking:**
- User says in natural language: "Lunch at Shaxian spent 45 CNY, paid via Alipay"
- AI Agent reads `AGENTS.md` + `QUICK-REFERENCE.md`
- AI Agent auto-creates: `Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`
- Dataview dashboard auto-updates

---

## 🚀 Quick Start

### AI Agent Integration

```bash
# Clone the repo
git clone https://github.com/lovepigpanda/obsidian-personal-finance-tracker.git

# Or copy zh/ or en/ folder to your Obsidian vault
cp -r zh/ /path/to/your-vault/
```

### Manual Human Entry

1. Install **Dataview** + **Templater** in Obsidian
2. Copy `zh/Templates/`, `zh/Dashboards/`, `zh/Accounts/`, `zh/Categories/` to vault
3. Templater → New Note → select template
4. Open `zh/Dashboards/finance-dashboard.md`

---

## 📊 Feature Summary

| Feature | Status | Note |
|---------|--------|------|
| Expense tracking | ✅ | Amount/category/account/payment/note |
| Income tracking | ✅ | Amount/source/account/note |
| Multi-account balance | ✅ | Auto-calculated |
| Multi-currency | ✅ | CNY/USD/EUR/JPY/HKD separate |
| Auto category mapping | ✅ | Keyword → category |
| Monthly summary | ✅ | Dataview auto |
| AI Agent support | ✅ | AGENTS.md + QUICK-REFERENCE.md |
| Bilingual (zh/en) | ✅ | Two versions |

---

## 🔗 Links

- **GitHub**: https://github.com/lovepigpanda/obsidian-personal-finance-tracker
- **License**: MIT