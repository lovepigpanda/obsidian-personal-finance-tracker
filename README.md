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
- 📅 **多币种汇率换算**（v1.1）
- 🏦 **银行 API 自动同步**（v2.0）

---

## 📁 项目结构

```
obsidian-personal-finance-tracker/
├── Templates/
│   ├── expense-template.md      # Templater 交互录入支出
│   └── income-template.md      # Templater 交互录入收入
├── Transactions/
│   ├── expenses/                # 支出文件（每笔一个 md）
│   └── incomes/                 # 收入文件
├── Dashboards/
│   └── finance-dashboard.md     # 主仪表盘
├── Accounts/
│   └── account-list.md          # 账户列表（含初始余额）
├── Categories/
│   ├── expense-categories.md     # 支出分类定义
│   ├── income-categories.md      # 收入分类定义
│   ├── expense-category-rules.md # 支出分类自动映射规则
│   └── income-category-rules.md  # 收入分类自动映射规则
└── README.md
```

---

## 🚀 快速开始

### 1. 环境要求

- **Obsidian**（v1.0+）
- **Dataview** 插件（必须）
- **Templater** 插件（必须）

### 2. 安装

1. 克隆本仓库到本地：
   ```bash
   git clone https://github.com/<YOUR_GITHUB_USERNAME>/obsidian-personal-finance-tracker.git
   ```

2. 将 `Templates/`、`Transactions/`、`Dashboards/`、`Accounts/`、`Categories/` 文件夹复制到你的 Obsidian vault 根目录

3. 在 Obsidian 中安装并启用 **Dataview** 和 **Templater** 插件

4. 配置 Templater：
   - 设置模板文件夹路径为 `Templates/`
   - 启用 "Create new note from template" 命令

### 3. 快速上手

1. 在 Obsidian 中按 `Ctrl/Cmd + P`，输入 `Templater: Create new note from template`
2. 选择 `expense-template.md` 录入支出，或 `income-template.md` 录入收入
3. 打开 `Dashboards/finance-dashboard.md` 查看财务概况

---

## 📖 使用指南

### 记录支出

1. 使用 Templater 创建新笔记 → 选择 `expense-template.md`
2. 系统会提示输入：日期（默认当天）、金额、币种、账户、支付方式、备注
3. **分类自动映射**：在备注中输入关键词（如"午餐"、"地铁"），系统自动推荐分类
4. 文件自动保存到 `Transactions/expenses/`，命名为 `YYYY-MM-DD-描述-金额-CURRENCY-ACTIVE.md`

### 记录收入

同上，选择 `income-template.md`

### 查看仪表盘

打开 `Dashboards/finance-dashboard.md`，包含：
- 本月收入/支出/余额汇总
- 各账户当前余额
- 支出/收入分类分布
- 最近 10 笔交易

### 自定义分类映射

编辑 `Categories/expense-category-rules.md`（支出）或 `Categories/income-category-rules.md`（收入），添加/修改关键词 → 分类映射规则。

### 添加新账户

编辑 `Accounts/account-list.md`，在账户表格中添加新行，并更新 Dataview 查询中的初始余额映射。

---

## 🔧 分类自动映射规则

当你在备注中输入特定关键词时，系统会自动 suggest 对应分类：

| 关键词 | 映射分类 |
|--------|---------|
| 午餐, 晚餐, 早餐, 外卖, 餐厅... | Food 🍔 |
| 地铁, 公交, 打车, 停车... | Transport 🚌 |
| 淘宝, 京东, 购物, 超市... | Shopping 🛍️ |
| 电影, 游戏, 音乐, 视频... | Entertainment 🎮 |
| 工资, 月薪, 薪资 | Salary 💰 |
| 兼职, 外快, 接单 | Freelance 💻 |

完整规则见：
- `Categories/expense-category-rules.md`
- `Categories/income-category-rules.md`

---

## 📊 仪表盘说明

### 主仪表盘（Finance Dashboard）

展示内容：
- **本月概要**：收入总额 / 支出总额 / 余额
- **各账户当前余额**（Dataview JS 自动计算）
- **支出分类分布**（GROUP BY category）
- **收入分类分布**
- **最近交易**
- **多币种分开统计**

### 月度报告

Dataview 实时查询，无需预生成。打开 `Dashboards/finance-dashboard.md` 即可看到当月数据。

---

## 🛠️ 插件依赖

| 插件 | 必须 | 说明 |
|------|------|------|
| Dataview | ✅ | 查询和渲染仪表盘 |
| Templater | ✅ | 交互式录入模板 |
| Commander | ❌ | 快捷命令（可选） |
| Obsidian Charts | ❌ | 趋势图展示（可选） |

---

## 🗂️ 文件命名规范

### 交易文件

格式：`YYYY-MM-DD-{描述}-{金额}-{CURRENCY}-{STATUS}.md`

示例：
- `2026-06-01-lunch-45-CNY-ACTIVE.md`（支出）
- `2026-06-01-salary-15000-CNY-ACTIVE.md`（收入）

### 状态说明

| 状态 | 说明 |
|------|------|
| ACTIVE | 活跃记录 |
| ARCHIVED | 已归档 |
| DELETED | 已删除（不计入统计） |

---

## 📝 自定义指南

### 添加新分类

1. 编辑 `Categories/expense-categories.md` 或 `Categories/income-categories.md`
2. 在表格中添加新分类行
3. 在对应的 `-category-rules.md` 中添加关键词映射

### 添加新账户

1. 编辑 `Accounts/account-list.md`
2. 在账户表格中添加新行
3. 在 `account-list.md` 的 Dataview JS 中添加新账户的初始余额

### 修改默认币种

编辑 `Templates/expense-template.md` 和 `Templates/income-template.md`，将 `currency` 默认值改为你需要的币种。

---

## ⚠️ 已知限制

1. 多币种汇率需要手动维护（v1.1 规划自动汇率获取）
2. 账户余额由 Dataview 实时计算，初始余额需在 `account-list.md` 中手动设置
3. 国内银行 API 暂不支持，自动同步功能延后（v2.0）

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT License