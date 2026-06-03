# obsidian-personal-finance-tracker

一套基于 Obsidian 的**个人财务追踪系统**（收入 + 支出 + 账户余额），每笔交易存为一个 md 文件，Dataview 驱动仪表盘，支持多币种、多账户、分类自动映射。

---

## ✨ 特性

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

本系统主要面向 **AI Agent**（Claude/Hermes 等 LLM），用户用自然语言描述一笔交易，AI Agent 自动：

1. 解析意图（支出/收入）、日期、金额、币种
2. 匹配账户和分类（根据 `QUICK-REFERENCE.md` 映射表）
3. 在 `Transactions/` 目录下创建对应 md 文件

**示例：**

用户 → `"今天午餐沙县花了45元，支付宝付款"`

AI Agent → 自动创建 `Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

详见：[AGENTS.md](AGENTS.md) · [QUICK-REFERENCE.md](QUICK-REFERENCE.md)

---

## 📁 项目结构

```
obsidian-personal-finance-tracker/
├── AGENTS.md                       # 🤖 AI Agent 使用指南（核心）
├── QUICK-REFERENCE.md             # 📋 AI Agent 快速参考（结构化映射表）
├── Templates/
│   ├── expense-template.md        # Templater 交互录入支出（人类使用）
│   └── income-template.md        # Templater 交互录入收入（人类使用）
├── Transactions/
│   ├── expenses/                  # 支出文件（AI Agent 创建）
│   └── incomes/                   # 收入文件（AI Agent 创建）
├── Dashboards/
│   └── finance-dashboard.md      # 主仪表盘（Dataview）
├── Accounts/
│   └── account-list.md            # 账户列表（含初始余额）
├── Categories/
│   ├── expense-categories.md      # 支出分类定义
│   ├── expense-category-rules.md # 支出分类关键词映射表
│   ├── income-categories.md       # 收入分类定义
│   └── income-category-rules.md  # 收入分类关键词映射表
└── README.md
```

---

## 🚀 快速开始

### AI Agent 接入（推荐）

1. 将本仓库克隆到本地（或将文件复制到 Obsidian vault）
2. AI Agent 读取 `AGENTS.md` 了解工作流程
3. AI Agent 参考 `QUICK-REFERENCE.md` 快速查找分类/账户映射
4. 用户用自然语言描述交易，AI Agent 自动创建文件

### 人类手动录入

1. 在 Obsidian 中安装 **Dataview** 和 **Templater** 插件
2. 复制 `Templates/`、`Dashboards/`、`Accounts/`、`Categories/` 到 vault
3. 用 Templater 创建新笔记 → 选择 `expense-template.md` 或 `income-template.md`
4. 打开 `Dashboards/finance-dashboard.md` 查看财务概况

---

## 📖 AI Agent 工作流

```
用户自然语言 → AI Agent 解析 → 匹配分类/账户 → 创建 md 文件 → 仪表盘自动更新
```

AI Agent 处理步骤：

1. **判断 type**：支出（"花了","买了"）→ `expense`，收入（"收到","进账"）→ `income`
2. **提取 date**：`今天` → `2026-06-01`，`昨天` → `2026-05-31`
3. **提取 amount + currency**：`45元` → `amount=45, currency=CNY`
4. **匹配 account**：支付工具 → `Alipay`/`WeChat Pay`/`CMB` 等
5. **匹配 category**：根据 note 关键词查 `QUICK-REFERENCE.md` 分类表
6. **生成文件名**：`{date}-{description}-{amount}-{currency}-ACTIVE.md`
7. **创建文件**：写入 `Transactions/expenses/` 或 `Transactions/incomes/`

---

## 🛠️ 插件依赖（人类手动录入）

| 插件 | 必须 | 说明 |
|------|------|------|
| Dataview | ✅ | 查询和渲染仪表盘 |
| Templater | ✅ | 交互式录入模板（人类使用） |
| Commander | ❌ | 快捷命令（可选） |
| Obsidian Charts | ❌ | 趋势图展示（可选） |

---

## 📋 AI Agent 快速参考

### 支出分类

| 分类 | 关键词 |
|------|--------|
| Food 🍔 | 午餐、晚餐、外卖、餐厅、沙县 |
| Transport 🚌 | 地铁、公交、打车、滴滴 |
| Shopping 🛍️ | 淘宝、京东、拼多多、超市 |
| Entertainment 🎮 | 电影、游戏、音乐、会员 |
| Health 💊 | 医院、药店、体检 |
| Education 📚 | 课程、书籍、培训 |
| Housing 🏠 | 房租、物业、水电 |
| Communication 📱 | 手机、话费、宽带 |
| Gift 🎁 | 红包、礼物、请客 |
| Travel ✈️ | 机票、酒店、旅游 |
| Investment 💹 | 理财、基金、股票 |
| Other ❓ | 其他 |

### 收入分类

| 分类 | 关键词 |
|------|--------|
| Salary 💰 | 工资、月薪、底薪 |
| Bonus 🎉 | 年终奖、奖金、绩效 |
| Freelance 💻 | 兼职、外快、接单 |
| Investment 📈 | 理财利息、投资收益 |
| Refund 🔄 | 退款、退货、补偿 |
| Gift 🎁 | 红包、礼金 |
| Other ❓ | 其他 |

### 账户

| 账户 | 关键词 |
|------|--------|
| Alipay | 支付宝 |
| WeChat Pay | 微信、微信支付 |
| CMB | 招行、招商银行 |
| ICBC | 工行、工商银行 |
| Credit Card | 信用卡 |
| Cash | 现金 |
| USD Account | 美元账户 |

---

## ⚠️ 已知限制

1. 多币种汇率需要手动维护（v1.1 规划自动汇率获取）
2. 账户余额由 `scripts/daily_integrity_check.py` 每日预计算为 `Accounts/balances.md` 快照, Dataview 只读快照 (性能 O(1))。初始余额需在 `account-list.md` 中手动设置。
3. 国内银行 API 暂不支持，自动同步功能延后（v2.0）

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT License