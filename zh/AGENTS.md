---
title: AI Agent — Natural Language Finance Tracking Guide
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: agent-guide
tags: [agent, finance, nlp, guide]
description: AI Agent 记账系统使用指南 — 如何解析自然语言输入并自动创建交易记录
---

# AI Agent 记账系统使用指南

> 本系统供 AI Agent（Claude/Hermes 等）使用，通过解析用户自然语言输入，自动创建收入/支出记录。

---

## 系统架构

```
用户自然语言输入
       ↓
AI Agent 解析意图 + 提取信息
       ↓
自动匹配分类（读取 category-rules）
       ↓
创建 md 文件（frontmatter + 内容）
       ↓
Dataview 仪表盘自动更新
```

---

## 工作流程

### 第一步：解析用户输入

用户用自然语言描述一笔交易，AI Agent 需提取以下字段：

| 字段 | 来源 | 示例 |
|------|------|------|
| `type` | 意图判断 | "花了"→expense，"收到"→income |
| `date` | 时间词 | "今天"→2026-06-01，"昨天"→2026-05-31 |
| `amount` | 数字提取 | "45元"→45，"15000"→15000 |
| `currency` | 币种 | "元"→CNY，"刀"→USD |
| `category` | 关键词匹配 | 见下方分类映射表 |
| `account` | 支付工具 | "支付宝"→Alipay，"微信"→WeChat Pay |
| `payment_method` | 支付方式 | 同 account 字段 |
| `note` | 原始描述 | 用户原话 |
| `status` | 固定值 | `ACTIVE` |

### 第二步：读取分类映射规则

AI Agent 读取以下文件获取关键词 → 分类映射：

- `Categories/expense-category-rules.md` — 支出分类（12类）
- `Categories/income-category-rules.md` — 收入分类（7类）

### 第三步：创建交易文件

**文件路径格式：**
```
Transactions/expenses/{YYYY-MM-DD}-{description}-{amount}-{CURRENCY}-{STATUS}.md
Transactions/incomes/{YYYY-MM-DD}-{description}-{amount}-{CURRENCY}-{STATUS}.md
```

**文件内容格式：**
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

| 字段 | 值 |
|------|---|
| **类型** | 支出 |
| **日期** | = this.date |
| **金额** | = this.amount |
| ... |
```

---

## 分类映射表（快速参考）

### 支出分类（Expense Categories）

| 分类 | 关键词示例 |
|------|-----------|
| Food 🍔 | 午餐、晚餐、早餐、外卖、餐厅、吃饭、快餐、沙县、火锅、烧烤 |
| Transport 🚌 | 地铁、公交、打车、滴滴、停车、加油、高铁、火车 |
| Shopping 🛍️ | 淘宝、京东、拼多多、购物、超市、衣服、鞋子 |
| Entertainment 🎮 | 电影、游戏、音乐、视频、爱奇艺、腾讯视频、steam、会员 |
| Health 💊 | 医院、药店、买药、体检、牙科 |
| Education 📚 | 课程、书籍、培训、考试、订阅 |
| Housing 🏠 | 房租、物业、水电、燃气、维修 |
| Communication 📱 | 手机、话费、宽带、流量 |
| Gift 🎁 | 红包、礼物、请客、人情 |
| Travel ✈️ | 机票、酒店、旅游、门票 |
| Investment 💹 | 理财、基金、股票（亏损） |
| Other ❓ | 其他、杂项 |

### 收入分类（Income Categories）

| 分类 | 关键词示例 |
|------|-----------|
| Salary 💰 | 工资、月薪、薪资、底薪 |
| Bonus 🎉 | 年终奖、奖金、绩效、分红 |
| Freelance 💻 | 兼职、外快、接单、私活 |
| Investment 📈 | 理财利息、投资收益、基金分红 |
| Refund 🔄 | 退款、退货、补偿 |
| Gift 🎁 | 红包、礼金 |
| Other ❓ | 其他、偶然收入 |

---

## 账户映射表（快速参考）

| 账户名 | 关键词 | 说明 |
|--------|--------|------|
| Alipay | 支付宝 | 支付宝 |
| WeChat Pay | 微信、微信支付 | 微信支付 |
| CMB | 招行、招商银行 | 招商银行 |
| ICBC | 工行、工商银行 | 工商银行 |
| Credit Card | 信用卡、贷记卡 | 信用卡 |
| Cash | 现金 | 现金 |
| USD Account | 美元账户、USD | 美元账户 |

### 转账关键词识别

| 触发词 | 意图 |
|--------|------|
| 转账 / 转给 / 转到 / 打给 | transfer |
| 转出 / 转入 | transfer（方向） |
| 调拨 / 调头寸 / 充值 / 提现 | transfer |
| 还信用卡 / 还卡 | transfer（出账→信用卡） |
| from X to Y / X 转 Y | transfer |

### 默认账户解析（V1.3.3+ #38）

如果用户在自然语言里**没指定账户**（例: "午餐沙县花了45元"），Agent 应调用 `scripts/transaction_create.py`，由其按以下优先级自动选账户：

1. **用户显式指定**（"用招行"）→ 直接用
2. **note 隐式提了账户名**（"用支付宝买了..."）→ 用 note 里的账户
3. **config/default_accounts.yaml 规则匹配**（"地铁|公交" → 交通卡，"还款" → CMB 储蓄卡，"Food/Shopping/..." → 信用卡）
4. **learning.json 历史偏好**（"沙县" → 上次用的账户）
5. **fallback**（expense=Alipay, income=CMB, transfer=ask 必须显式问）

**学习机制** (ask_on_2nd)：
- 第一次用默认账户 → 静默记录到 `~/.obsidian-finance/learning.json`
- 第二次同 keyword 但选了不同账户 → Agent 用 `clarify` 工具问用户"改默认吗?"
- 用户确认后 → 更新 learning

---

## 使用示例

### 示例 1：支出记账

**用户输入：**
> "今天午餐沙县花了45元，支付宝付款"

**AI Agent 处理：**
1. 判断 type = expense
2. 日期 = 今天 → 2026-06-01
3. 金额 = 45，币种 = CNY
4. 账户 = Alipay，支付方式 = Alipay
5. 关键词"午餐、沙县" → category = Food
6. note = "午餐-沙县小吃"

**创建文件：**
```
Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md
```

---

### 示例 2：收入记账

**用户输入：**
> "今天收到了6月份工资15000元，是招行发的"

**AI Agent 处理：**
1. 判断 type = income
2. 日期 = 今天 → 2026-06-01
3. 金额 = 15000，币种 = CNY
4. 账户 = CMB，支付方式 = Bank Transfer
5. 关键词"工资、薪资" → category = Salary
6. note = "6月工资"

**创建文件：**
```
Transactions/incomes/2026-06-01-salary-15000-CNY-ACTIVE.md
```

---

### 示例 3：多币种

**用户输入：**
> "在亚马逊买了本技术书花了35美元，信用卡支付"

**AI Agent 处理：**
1. type = expense
2. date = 今天 → 2026-06-01
3. amount = 35，currency = USD
4. account = Credit Card
5. 关键词"书、书籍" → category = Education
6. payment_method = Credit Card
7. note = "技术书-亚马逊"

**创建文件：**
```
Transactions/expenses/2026-06-01-book-35-USD-ACTIVE.md
```

---

### 示例 4：多币种收入

**用户输入：**
> "收到了 freelancing 的酬劳 500 美元，PayPal 到账"

**AI Agent 处理：**
1. type = income
2. date = 今天
3. amount = 500，currency = USD
4. account = PayPal
5. payment_method = PayPal
6. 关键词"freelancing、兼职、外快" → category = Freelance
7. note = "Freelancing 酬劳"

**创建文件：**
```
Transactions/incomes/2026-06-01-freelancing-500-USD-ACTIVE.md
```

---

### 示例 5：转账记账

**用户输入：**
> "从支付宝转 5000 到招行，还信用卡"

**AI Agent 处理：**
1. 判断 type = **transfer**（识别"转"+"还信用卡"）
2. 解析方向：from = Alipay，to = CMB
3. 金额 = 5000，币种 = CNY
4. category = Transfer（转账专用分类）
5. 生成配对 ID = `T-2026-06-01-xxx`
6. **创建 2 个文件**（out + in，共用同一个 `transfer_pair_id`）

**创建文件：**
```
Transactions/transfers/out/2026-06-01-transfer-out-Alipay-to-CMB-5000-CNY-ACTIVE.md
Transactions/transfers/in/2026-06-01-transfer-in-CMB-from-Alipay-5000-CNY-ACTIVE.md
```

**关键字段：**
```yaml
type: transfer
amount: 5000
currency: CNY
category: Transfer
from_account: Alipay
to_account: CMB
transfer_pair_id: T-2026-06-01-abc123
```

**查询配对：** 在 Obsidian 全局搜索 `transfer_pair_id: T-2026-06-01-abc123`，可同时定位 out 和 in 两个文件。

---

## AI Agent 操作检查清单

当用户要求记账时，AI Agent 应：

### 通用流程

- [ ] **1. 识别意图**：判断是支出（expense）/ 收入（income）/ 转账（transfer）
- [ ] **2. 提取日期**：将"今天/昨天/前天"转换为标准日期格式
- [ ] **3. 提取金额**：数字 + 币种（默认 CNY）
- [ ] **4. 提取账户**：支付工具 → 账户名（见账户映射表）
- [ ] **5. 匹配分类**：根据备注关键词匹配分类（见分类映射表）
- [ ] **6. 生成文件名**：`YYYY-MM-DD-{description}-{amount}-{CURRENCY}-ACTIVE.md`
- [ ] **7. 创建文件**：写入对应目录
- [ ] **8. 写入 frontmatter**：完整字段
- [ ] **9. 写入正文**：标准格式表格
- [ ] **10. 确认完成**：告诉用户文件路径和主要内容

### 转账专属流程

- [ ] **T1. 识别转账意图**：匹配"转/打/调拨/还信用卡/from X to Y"等触发词
- [ ] **T2. 解析 from/to 账户**：识别"X 转 Y"或"from X to Y"格式
- [ ] **T3. 生成配对 ID**：`T-{YYYY-MM-DD}-{随机串}`，out 和 in 共用同一 ID
- [ ] **T4. 创建 2 个文件**：`Transactions/transfers/out/` 和 `Transactions/transfers/in/`
- [ ] **T5. 写入配对字段**：`transfer_pair_id` 必须在两文件完全一致
- [ ] **T6. 提示用户配对 ID**：方便后续查询对端

---

## 注意事项

1. **日期格式**：统一使用 `YYYY-MM-DD`，如 `2026-06-01`
2. **金额**：纯数字，不含货币符号（如 `45` 而非 `¥45`）
3. **描述**：英文或拼音，用 `-` 连接（如 `lunch`、`subway`、`salary`）
4. **文件状态**：新建文件一律使用 `status: ACTIVE`
5. **多币种**：根据用户描述的币种如实记录，不转换
6. **关键词匹配**：优先匹配精准词（如"沙县"→Food），再匹配宽泛词（如"其他"→Other）
7. **账户选择**：如用户未指定账户，默认使用 `Alipay`（支出）或 `CMB`（收入）
8. **转账识别**：识别到"转/打/调拨"等触发词时，**必须**走 transfer 流程（创建 2 文件），不要当成支出或收入
9. **配对 ID 一致性**：转账 out 和 in 两个文件的 `transfer_pair_id` 必须**完全一致**，否则查询配对会失败
10. **配对 ID 唯一性**：每次转账用新的 `T-{date}-{随机串}`，避免历史数据冲突

---

## 文件位置参考

```
项目根目录/
├── AGENTS.md                         ← 本文件（AI Agent 使用指南）
├── Templates/                        ← Templater 模板（人类手动使用）
│   ├── expense-template.md
│   ├── income-template.md
│   └── transfer-template.md
├── Transactions/                     ← AI Agent 创建的文件目录
│   ├── expenses/
│   ├── incomes/
│   └── transfers/
│       ├── out/                      ← 转出文件
│       └── in/                       ← 转入文件
├── Dashboards/
│   └── finance-dashboard.md          ← Dataview 仪表盘
├── Categories/
│   ├── expense-category-rules.md     ← AI Agent 读取的分类规则
│   ├── income-category-rules.md
│   └── transfer-categories.md        ← 转账分类（仅 Transfer）
└── Accounts/
    └── account-list.md               ← 账户定义
```

---

## 相关文件

- [[Finance Dashboard]] — 查看所有交易汇总
- [[Account List]] — 账户余额查询
- [[Expense Categories]] — 支出分类完整说明
- [[Income Categories]] — 收入分类完整说明
- [[Transfer Categories]] — 转账分类说明
- [[expense-category-rules.md]] — 分类关键词映射（表格形式）
- [[income-category-rules.md]] — 收入分类关键词映射（表格形式）

---

> 本指南供 AI Agent 使用 | 创建于：2026-06-01 | 版本：V1.0