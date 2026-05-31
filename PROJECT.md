---
title: obsidian-personal-finance-tracker — Project Index
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: project-index
tags: [project, finance, obsidian]
---

# obsidian-personal-finance-tracker

> 个人财务追踪系统 / Personal Finance Tracker for Obsidian

## 📂 项目目录

```
obsidian-personal-finance-tracker-v1.0-ACTIVE/
├── SPEC.md                              # 项目规格文档（完整设计）
├── README.md                            # 项目说明（GitHub 首页）
├── Templates/
│   ├── expense-template.md             # 支出录入模板（含自动分类映射）
│   ├── expense-template-simple.md       # 支出录入模板（简化版，无自动映射）
│   └── income-template.md              # 收入录入模板（含自动分类映射）
├── Transactions/
│   ├── expenses/
│   │   └── 2026-06-01-lunch-45-CNY-ACTIVE.md  # 示例支出
│   └── incomes/
│       └── 2026-06-01-salary-15000-CNY-ACTIVE.md # 示例收入
├── Dashboards/
│   └── finance-dashboard.md            # 主仪表盘
├── Accounts/
│   └── account-list.md                 # 账户列表 + 余额自动计算
├── Categories/
│   ├── expense-categories.md          # 支出分类定义（含说明）
│   ├── income-categories.md            # 收入分类定义（含说明）
│   ├── expense-category-rules.md       # 支出分类关键词 → 分类映射规则
│   └── income-category-rules.md        # 收入分类关键词 → 分类映射规则
└── Scripts/
```

---

## 📋 核心文件说明

| 文件 | 用途 |
|------|------|
| `SPEC.md` | 完整项目规格（数据模型/架构/分类规则/仪表盘设计） |
| `README.md` | GitHub 仓库首页说明文档 |
| `Templates/expense-template.md` | Templater 交互录入支出（含自动分类映射 JS 脚本） |
| `Templates/income-template.md` | Templater 交互录入收入（含自动分类映射 JS 脚本） |
| `Dashboards/finance-dashboard.md` | 主仪表盘（Dataview 查询渲染） |
| `Accounts/account-list.md` | 账户列表 + Dataview JS 余额自动计算 |
| `Categories/expense-category-rules.md` | 支出关键词 → 分类映射规则（表格形式） |
| `Categories/income-category-rules.md` | 收入关键词 → 分类映射规则（表格形式） |

---

## 🎯 使用流程

```
1. Templater → 创建新笔记 → 选择 expense-template.md / income-template.md
2. 交互输入：描述 / 金额 / 币种 / 备注 / 账户
3. 自动映射：系统根据备注关键词自动 suggest 分类（可接受或手动选择）
4. 文件保存到 Transactions/expenses/ 或 Transactions/incomes/
5. 打开 Finance Dashboard 查看汇总
```

---

## 📦 插件依赖

- ✅ **Dataview** — 必须（查询渲染仪表盘）
- ✅ **Templater** — 必须（交互式模板录入）

---

## 🔗 关联

- 上一版本：无
- 下一版本：v1.1（多币种汇率自动获取）
- GitHub：https://github.com/<YOUR_GITHUB_USERNAME>/obsidian-personal-finance-tracker

---

## ✅ 完成清单

- [x] SPEC.md 项目规格文档
- [x] README.md 使用说明
- [x] 支出录入模板（含自动分类映射）
- [x] 收入录入模板（含自动分类映射）
- [x] 支出分类定义 + 关键词映射规则
- [x] 收入分类定义 + 关键词映射规则
- [x] 账户列表（含余额自动计算）
- [x] 主仪表盘（Dataview 查询）
- [x] 示例交易文件（支出 + 收入各一）
- [ ] GitHub 仓库初始化（待 Evan 提供 GitHub 用户名）
- [ ] 发布 v1.0

---

> 维护者：Evan | 创建于：2026-06-01 | License: MIT