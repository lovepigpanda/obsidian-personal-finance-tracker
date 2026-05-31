---
title: obsidian-personal-finance-tracker — Project Specification
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: project-spec
tags: [project, obsidian, finance, accounting]
github: https://github.com/<YOUR_GITHUB_USERNAME>/obsidian-personal-finance-tracker
license: MIT
---

## 1. 项目概述

### 1.1 是什么

一套基于 Obsidian 的**个人财务追踪系统**，每笔收入/支出存为一个 md 文件，Dataview 驱动仪表盘，支持多币种、多账户、分类自动映射、月度自动汇总报告。

### 1.2 目标用户

个人记账需求者。开源，主要给自己用，公开后希望收集反馈和贡献。

### 1.3 核心特性

- [x] 支出记录（金额/分类/账户/支付方式/备注）
- [x] 收入记录（金额/来源分类/账户/备注）
- [x] 多账户余额追踪
- [x] 多币种分别统计（不折算，分开显示）
- [x] 分类自动映射（输入关键词 → 自动 suggest 分类）
- [x] 月度汇总报告（Dataview 自动生成）
- [x] 主仪表盘（本月余额/分类占比/趋势）
- [ ] 多币种汇率换算（v1.1）
- [ ] 银行 API 自动同步（v2.0）

---

## 2. 架构

```
obsidian-personal-finance-tracker/
├── Templates/
│   ├── expense-template.md       # Templater 交互录入支出
│   └── income-template.md       # Templater 交互录入收入
├── Transactions/
│   ├── expenses/                # 支出文件（每笔一个 md）
│   │   └── YYYY-MM-DD-描述-金额-CURRENCY-ACTIVE.md
│   └── incomes/                 # 收入文件
│       └── YYYY-MM-DD-来源-金额-CURRENCY-ACTIVE.md
├── Dashboards/
│   ├── finance-dashboard.md     # 主仪表盘
│   └── monthly-report-YYYY-MM.md # 月度汇总报告（Dataview 自动生成）
├── Accounts/
│   └── account-list.md          # 账户列表（含初始余额）
├── Categories/
│   ├── expense-categories.md    # 支出分类定义（含关键词映射）
│   └── income-categories.md     # 收入分类定义（含关键词映射）
├── Scripts/
│   └── generate-monthly-report.py  # 可选：月度报告脚本（非必须）
└── README.md
```

---

## 3. 文件命名规范

### 3.1 交易文件名

格式：`YYYY-MM-DD-{描述}-{金额}-{CURRENCY}-{STATUS}.md`

示例：
- `2026-06-01-lunch-45-CNY-ACTIVE.md`
- `2026-06-01-salary-15000-CNY-ACTIVE.md`
- `2026-06-03-shopping-299-CNY-ACTIVE.md`

说明：
- 日期：交易日期（不是创建日期）
- 描述：英文或拼音（无空格，用 `-` 连接），简短有意义
- 金额：纯数字，单位为最小单位（如 45.00 表示 45 元）
- 币种：`CNY` / `USD` / `EUR` / `JPY` 等
- 状态：`ACTIVE`（活跃）/ `ARCHIVED`（归档）/ `DELETED`（删除）

### 3.2 月度报告文件

格式：`monthly-report-YYYY-MM.md`（Dataview 查询结果，实时渲染，不需要预生成）

---

## 4. Frontmatter 数据模型

### 4.1 支出交易（expense）

```yaml
---
type: expense
date: 2026-06-01
amount: 45
currency: CNY
category: Food           # 分类（来自 expense-categories.md）
subcategory: Lunch       # 子分类（可选）
account: Alipay          # 账户
payment_method: Alipay   # 支付方式
note: "午餐-沙县小吃"
tags: [expense, food]
status: ACTIVE
created: 2026-06-01
---
```

### 4.2 收入交易（income）

```yaml
---
type: income
date: 2026-06-01
amount: 15000
currency: CNY
category: Salary         # 分类（来自 income-categories.md）
account: CMB             # 账户（招商银行）
note: "6月工资"
tags: [income, salary]
status: ACTIVE
created: 2026-06-01
---
```

### 4.3 账户（account）

```yaml
---
account_name: Alipay
account_type: e-wallet    # bank/e-wallet/cash/credit-card
currency: CNY
initial_balance: 0
balance: 0                # 由 Dataview 自动计算，无需手动
note: "支付宝"
tags: [account]
status: ACTIVE
---
```

---

## 5. 分类体系

### 5.1 默认支出分类

| 分类 | 关键词（自动映射） |
|------|-----------------|
| Food | 午餐, 晚餐, 早餐, 外卖, 餐厅, 吃饭, 餐饮, 沙县, 兰州, 快餐 |
| Transport | 地铁, 公交, 打车, taxi, uber, 停车, 加油, 高铁, 火车 |
| Shopping | 淘宝, 京东, 拼多多, 购物, 衣服, 鞋子, 超市 |
| Entertainment | 电影, 游戏, 音乐, 视频, 爱奇艺, 腾讯视频, steam |
| Health | 医院, 药店, 买药, 体检, 牙科, 中医 |
| Education | 课程, 学费, 书籍, 培训, 考试, 订阅 |
| Housing | 房租, 物业, 水电, 燃气, 维修 |
| Communication | 手机, 话费, 宽带, 流量 |
| Gift | 红包, 礼物, 请客, 人情 |
| Travel | 机票, 酒店, 旅游, 门票 |
| Other | 其他, 杂项 |

### 5.2 默认收入分类

| 分类 | 关键词 |
|------|------|
| Salary | 工资, 月薪, 薪资, 底薪 |
| Bonus | 年终奖, 奖金, 绩效, 分红 |
| Freelance | 兼职, 外快, 接单, 私活 |
| Investment | 理财, 利息, 投资收益, 基金, 股票 |
| Refund | 退款, 退货, 补偿 |
| Other | 其他, 偶然收入 |

### 5.3 分类映射规则（category-rules.md）

通过 `category-rules.md` 文件维护关键词 → 分类映射，模板录入时 Templater 脚本根据 note 输入自动 suggest 分类。

格式：
```yaml
# 支出映射
lunch -> Food
外卖 -> Food
地铁 -> Transport
打车 -> Transport
淘宝 -> Shopping
京东 -> Shopping
```

---

## 6. 账户体系

### 6.1 默认账户

| 账户名 | 类型 | 默认币种 |
|--------|------|---------|
| Cash | cash | CNY |
| Alipay | e-wallet | CNY |
| WeChat Pay | e-wallet | CNY |
| CMB | bank | CNY |
| ICBC | bank | CNY |
| Credit Card | credit-card | CNY |
| USD Account | bank | USD |

### 6.2 账户余额计算

余额 = 初始余额 + SUM(收入) - SUM(支出)

Dataview 按 account 字段 group by 计算每个账户的当前余额。

---

## 7. 仪表盘

### 7.1 主仪表盘（finance-dashboard.md）

展示内容：
1. **本月概要**：收入总额 / 支出总额 / 余额
2. **各账户当前余额**
3. **支出分类分布**（GROUP BY category，金额求和）
4. **收入分类分布**（GROUP BY category，金额求和）
5. **最近 10 笔交易**
6. **本月支出趋势**（每日汇总）
7. **多币种分开统计**（GROUP BY currency）

### 7.2 月度报告（monthly-report-YYYY-MM.md）

每个自然月结束后生成，包含：
- 收入支出汇总
- 分类明细
- 各账户余额变化
- 与上月对比

---

## 8. 插件依赖

- **Dataview**（必须）：查询和渲染仪表盘
- **Templater**（必须）：交互式录入模板
- **Commander**（可选）：快捷命令
- **Obsidian Charts**（可选）：趋势图展示

---

## 9. 版本历史

| 版本 | 日期 | 状态 | 说明 |
|------|------|------|------|
| V1.0 | 2026-06-01 | DRAFT | 初始版本，完成基本框架设计 |

---

## 10. 已知限制

1. 多币种汇率需要手动维护（v1.1 规划自动汇率获取）
2. 账户余额由 Dataview 实时计算，初始余额需在 account-list.md 中手动设置
3. 国内银行 API 暂不支持，自动同步功能延后（v2.0）