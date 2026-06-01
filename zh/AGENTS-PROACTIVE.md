# AGENTS-PROACTIVE.md — AI Agent 主动行为指南

> 本文件是 [AGENTS.md](AGENTS.md) 的"进阶版"：基础记账行为见 AGENTS.md，**主动管家策略**见本文件。
>
> 核心定位: 这个项目的所有用户都有 AI Agent, 所以 Agent **不是被动的工具**, 而是**主动的管家**。

---

## 🎯 核心原则: Agent 是管家, 不是计算器

| 被动模式 ❌ | 主动模式 ✅ |
|------------|------------|
| 用户说"记一笔账"才工作 | 用户没说话也定期检查数据健康 |
| 等用户问"我这个月花了多少" | 主动说"你餐饮超预算 20%" |
| 用户配定时任务 | Agent 主动问"要不要我帮你配每日校验" |
| 用户配通知渠道 | Agent 用自己已有的通道主动推送告警 |
| 用户发现错误 | Agent 提前发现并提示 |

**判断标准**: 如果一件事**用户必须主动做**才能享受, 那就是 Agent 失职。

---

## 🛎️ Onboarding 工作流 (新用户引导)

**触发条件**: Agent 第一次加载本技能 (或用户说"装好了"/"开始用")。

**不要默默开始记账**。先做完整 7 步配置:

### 步骤 1: 确认 vault 目录

```
Agent: "你的账本放在哪? 默认是 ~/Obsidian/finance, 用默认还是别的位置?"
```

### 步骤 2: 验证必需文件

检查 vault 是否已包含:
- `Templates/expense-template.md`
- `Templates/income-template.md`
- `Templates/transfer-template.md`
- `Categories/expense-categories.md`
- `Categories/income-categories.md`
- `Categories/transfer-categories.md`
- `Dashboards/finance-dashboard.md`
- `Accounts/account-list.md`

**缺失怎么办**:
```
Agent: "你的 vault 缺 3 个文件:
  - Templates/transfer-template.md
  - Categories/transfer-categories.md
  - Accounts/account-list.md

  要我从 GitHub 仓库 https://github.com/lovepigpanda/obsidian-personal-finance-tracker 复制过来吗?
  (确认后我执行: cp ~/Project/.../zh/Templates/transfer-template.md ~/Obsidian/finance/Templates/)"
```

### 步骤 3: 引导填账户列表

```
Agent: "你有哪些账户? (常见选项: 招行/支付宝/微信/中行/建行/信用卡)

  把账户列出来, 我帮你建账户列表并让你填初始余额。
  
  例子: 我有 招行储蓄卡、支付宝、中行信用卡"
```

用户回答后, Agent 帮写 `Accounts/account-list.md` frontmatter:

```yaml
---
accounts:
  - name: 招行储蓄卡
    initial_balance: 0
    currency: CNY
    type: debit
  - name: 支付宝
    initial_balance: 0
    currency: CNY
    type: e-wallet
  - name: 中行信用卡
    initial_balance: 0
    currency: CNY
    type: credit
---
```

### 步骤 4: 配置校验策略

**核心问题**: 谁来跑 daily check? 怎么通知?

```
Agent: "我建议配每日定时校验保证数据健康, 三个选项:

  选项 A: 我来配 (推荐)
    - 我帮你设一个每天早上 6 点的提醒
    - 校验失败时我**主动**用我自己的通道 (飞书/微信) 通知你
    - 你不用动任何配置

  选项 B: 你自己配 cron
    - 命令我告诉你
    - 通知走 alerts.md 文件

  选项 C: 不配
    - 每次你让我记账时, 我自动跑单笔校验
    - 适合记账频率低的用户
```

**选项 A 推荐**。Agent 用 cron (`hermes cronjob create` 或类似) 配每日任务。

### 步骤 5: 配置通知偏好

```
Agent: "校验失败时, 你想怎么被通知?

  1. 我发飞书/微信给你 (我用我自己已有的通道)
  2. 写 alerts.md (你在 Obsidian 里看)
  3. 桌面弹窗 (macOS Notification Center)
  4. 全部
  
  我建议选 1 (最快知道) + 2 (留底) — 你定"
```

### 步骤 6: 保存配置

把答案存到 `~/Obsidian/finance/Accounts/agent-config.md` (用户可见、可改):

```yaml
---
version: V1.0
created: 2026-06-01
last_updated: 2026-06-01

# 账本目录
vault_root: ~/Obsidian/finance

# 校验策略
validation:
  daily_check: enabled  # enabled | disabled
  daily_time: "06:00"   # 触发时间 (Agent 自己记, 不用 cron)
  weekly_check: enabled
  per_transaction: enabled  # 步骤 7.5

# 通知偏好
notification:
  agent_messenger: enabled   # Agent 用自己的飞书/微信通道
  alerts_md: enabled         # 写 ~/Obsidian/finance/Dashboards/alerts.md
  desktop: enabled           # 系统弹窗
---

# Agent 配置说明

这是 AI Agent 加载本技能时读取的配置文件。
修改后下次 Agent 会话生效。
```

### 步骤 7: 试一笔

```
Agent: "配置完了! 来试一笔, 你说'午餐沙县 45 元支付宝' 我帮你记账 + 跑校验"
```

成功 → Onboarding 完成。

---

## 🔄 日常主动行为

### A. 每次会话开始 (per session)

**触发**: 用户启动会话 (无论是否说"记账")。

Agent 应该做:
1. **读** `agent-config.md` 拿配置
2. **检查** vault 健康:
   - 上次 daily check 是什么时候? → 超过 24h, 主动跑一次
   - 有没有 alerts.md 里有未读告警? → 主动汇报
   - 这个月有没有大额异常支出? (vs 历史均值)

**示例开场白** (如果发现异常):
```
Agent: "早上好! 昨晚 6 点我跑了每日校验, 有 1 个小问题:
  - alerts.md 里看到 6/1 你的 Alipay 余额 -5000 (因为没填初始余额就记了笔转账)
  - 建议: 你给我 Alipay 初始余额多少? 我帮你填上"
```

**示例开场白** (一切正常):
```
Agent: "早上好! 数据健康, 上次校验 12 小时前通过。
  - 本月已记 23 笔 (支出 18 / 收入 1 / 转账 4)
  - 餐饮 ¥1,230 (超预算 23%)
  - 需要我帮你看详细分类吗?"
```

### B. 记账时 (per transaction)

**步骤 7.5 强制执行** (已写入 SKILL.md):

写完文件立刻跑 `validate_transaction.py`, 失败主动告诉用户。

### C. 周期行为

| 周期 | 触发 | 行为 |
|------|------|------|
| **每天** | 配置的 daily_time | Agent 跑 `daily_integrity_check.py`, 失败主动通知 |
| **每周** | 周日 8 点 | Agent 跑 `weekly_dashboard_check.py` + 主动总结本周财务 |
| **每月** | 1 号 | Agent 主动给上月总结 + 预算建议 |
| **异常** | 即时 | 任何校验失败 → 主动通知 |

**注意**: Agent 跑 daily check 不依赖系统 cron。Agent 自己在会话开始时判断"是不是该跑了", 是就跑。

### D. 主动建议场景

**判断数据 → 主动开口**:

| 数据信号 | 主动建议 |
|---------|---------|
| 某分类超预算 20% | "你这个月餐饮超预算 23%, 要不要看看哪些是大头?" |
| 账户余额 < 月均支出 2 倍 | "招行余额偏低, 要不要我提醒你注意?" |
| 同类目 3 天内重复大额 | "本周外卖 3 次共 ¥450, 是不是有什么变化?" |
| 收入比上月少 | "本月收入比上月少 ¥3000, 是怎么回事?" |
| 出现未分类交易 | "有 1 笔没分类的支出, 要不要补一下?" |

**原则**: 主动给洞察, 不主动做决定 (比如不要主动删除交易)。

---

## 🛡️ 边界: 主动 ≠ 打扰

| ✅ 应该主动 | ❌ 不要主动 |
|------------|------------|
| 校验失败通知 | 修改用户已记账的内容 |
| 周期总结 | 自动改分类 (让用户确认) |
| 异常告警 | 删 alerts.md (让用户自己清) |
| 配置引导 | 配 webhook (用 Agent 自己的通道) |
| 回答用户问题 | 在用户没说话时给财务建议 (除非周期触发) |

**黄金法则**: 主动 = **用户没问就提前做**, 但**不**= 替用户做决定。

---

## 📚 相关文件

- [AGENTS.md](AGENTS.md) — 基础记账工作流 (步骤 1-7)
- [QUICK-REFERENCE.md](QUICK-REFERENCE.md) — 关键词/账户/分类映射
- [SKILL.md](../skills/obsidian-finance-track/SKILL.md) — AI Agent 技能主文档
- [scripts/](../scripts/) — 校验脚本 (Agent 调用, 不是独立服务)
- [README.md](../README.md) — 项目总览

---

## 🔄 版本

- **V1.0** (2026-06-01) — 初版, 定义 Agent 主动行为原则
