---
title: obsidian-personal-finance-tracker — Project Specification
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: project-spec
tags: [project, obsidian, finance, accounting]
github: https://github.com/lovepigpanda/obsidian-personal-finance-tracker
license: MIT
---

# obsidian-personal-finance-tracker — Project Specification
# 项目规格文档

---

## 版本信息 / Version Info

| 字段 / Field | 值 / Value |
|--------------|-----------|
| 项目名 / Project | obsidian-personal-finance-tracker |
| 版本 / Version | V1.0 |
| 状态 / Status | ACTIVE |
| 创建日期 / Created | 2026-06-01 |
| 更新日期 / Updated | 2026-06-01 |
| GitHub | https://github.com/lovepigpanda/obsidian-personal-finance-tracker |
| License | MIT |

---

## 项目结构 / Project Structure

```
obsidian-personal-finance-tracker/
├── README.md                       # 双语入口 / Bilingual entry point
├── LICENSE                         # MIT License
├── SPEC.md                         # 本规格文档 / This specification
├── PROJECT.md                      # 项目索引 / Project index
├── zh/                             # 🌏 中文版（主要版本）/ Chinese version (primary)
│   ├── AGENTS.md                   # 🤖 AI Agent 使用指南
│   ├── QUICK-REFERENCE.md          # 📋 AI Agent 快速参考
│   ├── Templates/
│   ├── Transactions/
│   ├── Dashboards/
│   ├── Accounts/
│   └── Categories/
├── en/                             # 🌎 English version
│   ├── AGENTS.md                   # 🤖 AI Agent guide
│   ├── QUICK-REFERENCE.md          # 📋 AI Agent quick reference
│   ├── Templates/
│   ├── Transactions/
│   ├── Dashboards/
│   ├── Accounts/
│   └── Categories/
└── Scripts/
```

---

## 核心设计 / Core Design

### 技术选型 / Technology Stack

- **存储**: Obsidian Markdown 文件（每笔交易一个 `.md`）
- **查询**: Dataview（实时查询 + 仪表盘渲染）
- **模板**: Templater（人类手动录入交互）
- **插件依赖**: Dataview ✅, Templater ✅（人类）, Commander ❌, Charts ❌

### 多语言版本策略 / Multi-language Strategy

- **zh/**: 中文关键字为主，英文关键字为辅（适合中文用户 + AI Agent）
- **en/**: 英文关键字为主，中文关键字为辅（适合英文用户 + AI Agent）
- **AI Agent**: 根据用户输入语言自动选择对应版本

### 多币种策略 / Multi-currency Strategy

- **分开统计**: CNY / USD / EUR / JPY / HKD 分别显示，不折算
- **手动汇率**: 汇率需在 `QUICK-REFERENCE.md` 中手动维护（v1.1 计划自动获取）
- **文件命名**: 金额后缀币种代码，如 `45-CNY`, `35-USD`

### 账户余额计算 / Account Balance Calculation

- **初始余额**: 用户在 `Accounts/account-list.md` 中手动设置
- **预计算快照**: `scripts/daily_integrity_check.py` 每日扫所有交易, 写入 `Accounts/balances.md` 快照。Dataview 读快照 (O(1)), 不再每次打开全扫描。算法: `initial_balance + sum(income) - sum(expense) - sum(transfer-out) + sum(transfer-in)`, 见 `scripts/lib/balance.py`
- **多币种**: 各币种分别计算，不混算

---

## 分类体系 / Category System

### 支出分类 / Expense Categories (12 类)

| 分类 | 英文 | Emoji | zh 关键词 | en 关键词 |
|------|------|-------|---------|-----------|
| Food | Food | 🍔 | 午餐晚餐早餐外卖餐厅吃饭 | lunch dinner breakfast takeout restaurant |
| Transport | Transport | 🚌 | 地铁公交打车滴滴停车加油 | subway bus taxi uber parking gas |
| Shopping | Shopping | 🛍️ | 淘宝京东拼多多超市购物衣服 | Taobao JD Pinduoduo supermarket shopping |
| Entertainment | Entertainment | 🎮 | 电影游戏音乐视频会员Steam | movie game music video Netflix Steam |
| Health | Health | 💊 | 医院药店体检牙科门诊 | hospital pharmacy checkup dental |
| Education | Education | 📚 | 课程书籍培训考试订阅 | course book training exam subscription |
| Housing | Housing | 🏠 | 房租物业水电燃气维修 | rent property utilities repair |
| Communication | Communication | 📱 | 手机话费宽带流量 | phone broadband data |
| Gift | Gift | 🎁 | 红包礼物请客人情 | red envelope gift treat |
| Travel | Travel | ✈️ | 机票酒店旅游门票 | flight hotel travel ticket |
| Investment | Investment | 💹 | 理财基金股票投资亏损 |理财 fund stock investment loss |
| Other | Other | ❓ | 其他杂项 | other miscellaneous |

### 收入分类 / Income Categories (7 类)

| 分类 | 英文 | Emoji | zh 关键词 | en 关键词 |
|------|------|-------|---------|-----------|
| Salary | Salary | 💰 | 工资月薪薪资底薪 | salary wages base pay |
| Bonus | Bonus | 🎉 | 年终奖奖金绩效分红 | year-end bonus performance dividend |
| Freelance | Freelance | 💻 | 兼职外快接单私活 | freelance side job gig |
| Investment | Investment | 📈 | 理财利息投资收益基金分红 | investment interest fund dividend |
| Refund | Refund | 🔄 | 退款退货补偿赔偿 | refund return compensation |
| Gift | Gift | 🎁 | 红包礼金 | red envelope gift money |
| Other | Other | ❓ | 其他偶然收入 | other incidental income |

---

## AI Agent 工作流 / AI Agent Workflow

```
用户自然语言 / User natural language
       ↓
AI Agent 解析 / AI Agent parses
       ↓
匹配分类（读 category-rules）/ Match category (read category-rules)
       ↓
创建 md 文件 / Create .md file
       ↓
Dataview 仪表盘自动更新 / Dataview dashboard auto-updates
```

AI Agent 处理步骤 / AI Agent Steps:
1. 判断 type：支出/收入
2. 提取 date：时间词 → YYYY-MM-DD
3. 提取 amount + currency：数字 + 币种
4. 匹配 account：支付工具 → 账户名
5. 匹配 category：根据 note 关键词查分类表
6. 生成 filename：`{date}-{desc}-{amount}-{currency}-ACTIVE.md`
7. 写入 `Transactions/expenses/` 或 `Transactions/incomes/`

---

## 文件命名规范 / File Naming Convention

### 支出文件 / Expense Files
```
Transactions/expenses/{YYYY-MM-DD}-{description}-{amount}-{CURRENCY}-{STATUS}.md
```
示例 / Example: `Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

### 收入文件 / Income Files
```
Transactions/incomes/{YYYY-MM-DD}-{description}-{amount}-{CURRENCY}-{STATUS}.md
```
示例 / Example: `Transactions/incomes/2026-06-01-salary-15000-CNY-ACTIVE.md`

---

## Frontmatter Schema

```yaml
---
type: expense                    # or income
date: YYYY-MM-DD
amount: number
currency: CNY                    # CNY/USD/EUR/JPY/HKD
category: CategoryName
account: AccountName
payment_method: PaymentMethod
note: "User's raw description"
tags: [expense, categoryName]    # expense or income + category name
status: ACTIVE
created: YYYY-MM-DD
---
```

---

## 已知限制 / Known Limitations

1. 多币种汇率需手动维护（v1.1 计划自动获取）
2. 账户余额由 `scripts/daily_integrity_check.py` 每日预计算为 `Accounts/balances.md` 快照, Dataview 只读快照 (性能 O(1))。初始余额需在 `zh/Accounts/account-list.md` 中手动设置
3. 国内银行 API 暂不支持，自动同步功能延后（v2.0）

---

## 未来规划 / Future Plans

- v1.1: 多币种自动汇率获取
- v2.0: 银行 API 自动同步
- 收入支出分类自定义扩展
- 年度财务报表