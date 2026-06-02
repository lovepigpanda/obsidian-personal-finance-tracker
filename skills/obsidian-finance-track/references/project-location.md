# Obsidian Finance Track — 项目定位参考

## ⚠️ 核心原则：技能与数据分离

```
技能代码（可 GitHub 同步）
  ~/Project/obsidian-personal-finance-tracker/
  └── zh/AGENTS.md, QUICK-REFERENCE.md, Templates/, Categories/

账本数据（本地私有，不上传）
  ~/Obsidian/finance/
  └── Transactions/, Accounts/, Dashboards/
```

**Transaction 文件永远在 ~/Obsidian/finance/，不是项目目录里。**

---

## 项目路径（Skill 代码）

| 环境 | 路径 |
|------|------|
| macOS | `/Volumes/Evan2T/Project/obsidian-personal-finance-tracker-v1.0-DRAFT/zh/` |
| 标准 | `~/Project/obsidian-personal-finance-tracker/zh/` |
| GitHub | `https://github.com/lovepigpanda/obsidian-personal-finance-tracker` |

## 账本数据路径

```
~/Obsidian/finance/
├── Transactions/
│   ├── expenses/           ← AI Agent 创建的支出文件
│   └── incomes/            ← AI Agent 创建的收入文件
├── Accounts/account-list.md
├── Templates/              ← Templater 模板
├── Categories/             ← 分类规则
└── Dashboards/finance-dashboard.md
```

## 项目结构（技能代码，不含 Transaction 数据）

```
zh/
├── AGENTS.md                       # AI Agent 工作流（必读）
├── QUICK-REFERENCE.md              # 结构化参考（必读）
├── Templates/expense-template.md  # Templater 支出模板
├── Templates/income-template.md   # Templater 收入模板
├── Categories/expense-category-rules.md
├── Categories/income-category-rules.md
├── Accounts/account-list.md        # ← 账本数据，在 ~/Obsidian/finance/
└── Dashboards/finance-dashboard.md # ← 账本数据，在 ~/Obsidian/finance/
```

## 版本

- **GitHub**: lovepigpanda/obsidian-personal-finance-tracker
- **版本**: V1.0（双语：zh/ + en/）
- **License**: MIT
- **验证日期**: 2026-06-01