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
| 用户配定时任务 | **Agent 帮用户配** (生成 plist/cron, 用户复制粘贴) |
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

### 步骤 4: 配置定时任务 (V1.1 升级版)

**核心问题**: 谁负责把校验/提醒跑起来? Agent 必须主动帮用户配定时任务, 因为 Agent 关闭会话后就不能主动提醒了。

```
Agent: "我帮你配 5 个定时任务, 跑校验 + 提醒。要不要我帮你生成 launchd plist / crontab?
  你只要复制粘贴到终端就行。

  - 每日 18:00  跑 daily_integrity_check.py (含 #33 频率检测、#34 账户遗忘)
  - 每周日 20:00  跑 weekly_summary.py (#35 周末复盘)
  - 每月最后一日 21:00  跑 monthly_summary.py (#36 月末自检)
  - 每日 8:00   跑 credit_card_reminder.py (#23 信用卡还款)
  - 每日 8:05   跑 installment_check.py (#24 分期到期)

  不配的话, 校验/提醒只在咱俩对话时跑——你不开会话, 我就不能主动提醒你。"
```

**为什么必须配定时任务**:
- Agent 只在**用户开会话**时在线, 关掉会话 Agent 就"睡"了
- 想让 Agent 主动提醒 ("该还款了"/"今天没记账"), 必须在**指定时间被唤醒**——只有系统定时任务能保证
- Agent 的责任是**主动帮用户配** (生成 plist/cron, 用户复制粘贴), 不是"绕开"定时任务

**生成 plist 示例 (macOS launchd)**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.user.finance-daily-check</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/你的用户名/Project/obsidian-personal-finance-tracker/scripts/daily_integrity_check.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
    <key>StandardOutPath</key><string>/tmp/finance-daily.log</string>
    <key>StandardErrorPath</key><string>/tmp/finance-daily.err</string>
</dict>
</plist>
```

保存到 `~/Library/LaunchAgents/com.user.finance-daily-check.plist`, 然后:
```bash
launchctl load ~/Library/LaunchAgents/com.user.finance-daily-check.plist
```

**配置存到 agent-config.md** (用户可见、可改):
```yaml
scheduled_tasks:
  daily_18_integrity: enabled      # daily_integrity_check.py
  weekly_sun_20_summary: enabled   # weekly_summary.py
  monthly_last_21_summary: enabled # monthly_summary.py
  daily_08_credit_card: enabled    # credit_card_reminder.py
  daily_0805_installment: enabled  # installment_check.py
```

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

**注意**: Agent 跑 daily/weekly/monthly 任务**必须**依赖系统 cron/launchd, 否则 Agent 关掉会话就不提醒了。
Agent 的责任是**主动帮用户配** (生成 plist/cron, 用户复制粘贴), 不是"绕开"定时任务。

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

## 🆕 V1.1 新增的 6 个主动行为

V1.0 阶段定义了"主动"的原则, V1.1 把它落地成 6 个**具体可调用的脚本 + Agent 责任**。每段都是"触发 → Agent 行为 → 边界 → 失败兜底"四件套。

### F. #23 信用卡还款提醒 — `credit_card_reminder.py`

**触发**: 用户配置每日 8:00 定时任务 (Agent 帮生成 launchd plist, 复制粘贴即用)。

**Agent 责任**:
1. **首次 Onboarding 时** (SKILL.md 步骤 3 扩展): 询问每张信用卡的 `statement_day` + `payment_due_day`, 写入 `Accounts/account-list.md` 的 frontmatter
2. **每天定时任务触发后**: 读 `alerts.md`, 把 WARN 级别的"X 卡 3 天后还款"用自己通道 (飞书/微信) 主动推给用户
3. **逾期 (ERROR)** 立即推 (不等用户问)

**脚本做什么**:
- 扫 `Accounts/account-list.md` 找 `type: credit` 的账户
- 对每张卡算下次出账日 + 还款日 (处理跨月/月末)
- 还款日 ≤ 5 天 → WARN, 已过 → ERROR
- 写到 `alerts.md`

**边界**:
- ❌ 不要自动还款 (那是银行 App 的事)
- ❌ 不要修改用户的卡片信息
- ✅ 只读 + 提醒

**失败兜底**:
- 找不到 `statement_day`/`payment_due_day` → INFO 提示用户补字段 (软告警, 不阻塞)
- `alerts.md` 写失败 → 桌面通知 + 日志

---

### G. #24 分期完整性检查 — `installment_check.py` + `installment_helper.py`

**触发**: 用户写完第一期 expense 后 (调 helper) + 每日 8:05 定时 (调 check)。

**Agent 责任**:
1. **用户说"我买了 iPhone 24 期每月 500"**: Agent 先写第一期 expense, 立即调 `installment_helper.py create --first-file <第一期> --total 24`, 自动生成剩余 23 期 PENDING 模板
2. **每天 8:05**: 调 `installment_check.py`, 扫所有分期组
3. **发现 PENDING 到期 (今天 ≥ 该扣款日)**: 主动问"iPhone 第 5 期今天该扣了, 我帮你改 status=ACTIVE 吗?"
4. **发现分期组缺期 / 字段不一致**: ERROR 告警

**脚本做什么**:
- `helper`: 从第一期 frontmatter 复制 amount/currency/account/category, 生成 N-1 个 PENDING 模板, 日期递增
- `check`: 按 `installment_group_id` 分组, 校验 ① 总期数 ② 字段一致性 ③ PENDING 是否到期 ④ 孤立分期 (只有 1 期但标记分期)

**边界**:
- ❌ 不要自动把 PENDING 改 ACTIVE (扣款真的发生了吗? 需用户确认)
- ❌ 不要补缺失的期 (用户可能主动停止分期, 不能擅自生成)
- ✅ 只检查 + 提醒

**失败兜底**:
- 第一期 frontmatter 缺 `installment_group_id` → helper 自动生成 `INS-{date}-{account}-{amount}`
- 缺期 → ERROR 列出缺的期号, 用户决定补还是删

---

### H. #33 记账频率检测 — 嵌入 `daily_integrity_check.py`

**触发**: 每天 18:00 定时 (与 daily check 一起跑)。

**Agent 责任**:
1. 读脚本输出, 看有没有"过去 7 天 0 笔交易" (但账户余额非零) 的 WARN
2. 主动推: "你过去 7 天 0 笔记账, 但账户余额 X, 要不要打开银行 App 核对?"
3. 周末 (周六/周日) 不推 (避免打扰)

**脚本做什么** (实际实现, 在 `daily_integrity_check.py:check_bookkeeping_frequency`):
- 扫过去 7 天 ACTIVE 交易
- 0 笔 + 至少 1 个账户有非零余额 → WARN (可能漏记)
- 否则 INFO 输出"7 天记账: N 笔 / 活跃 M 天"

**边界**:
- ❌ 不要自动建占位交易
- ❌ 节假日/出差不要推 (识别不了, 推了用户自己 ignore)

---

### I. #34 账户遗忘检测 — 嵌入 `daily_integrity_check.py`

**触发**: 每天 18:00 定时 (与 daily check 一起跑)。

**Agent 责任**:
1. 读脚本输出, 看有没有"某账户 N 天没动" (N>14) 的 WARN
2. 主动推: "招行储蓄卡已 18 天无变动, 这个账户还在用吗?"
3. 现金账户/低频账户可豁免 (用户标记 `low_frequency: true`)

**脚本做什么** (实际实现, 在 `daily_integrity_check.py:check_account_inactivity`):
- 按账户聚合最后 ACTIVE 交易日期 (含 transfer 端)
- 距今 > 14 天 → WARN ("账户 X 已 N 天无变动, 这个账户还在用吗?")
- 标记 `low_frequency: true` 的账户跳过

**边界**:
- ❌ 不要自动归档"遗忘"账户
- ✅ 只提醒

---

### J. #35 周末复盘 — `weekly_summary.py`

**触发**: 每周日 20:00 定时任务 (Agent 帮配)。

**Agent 责任**:
1. 定时触发后, 读 `alerts.md` 拿本周汇总
2. 主动推飞书/微信: "本周你记了 23 笔, 餐饮 ¥820 (上周 ¥1,200, 降 32%), 整体不错!"
3. 用户问"上周花了多少" 时, 直接调脚本 (不依赖定时)

**脚本做什么**:
- 范围: 本周一 00:00 ~ 本周日 23:59
- 输出: 笔数 / 总支出 / 总收入 / 分类前 3 / 账户余额变化 / vs 上周同比
- 写到 `alerts.md`

**边界**:
- ❌ 不要给"省钱建议" (Agent 是记账管家, 不是理财顾问)
- ✅ 给数据 + 给对比

**失败兜底**:
- 本周 0 笔 → 仍输出空周报 (笔数=0), 不报错

---

### K. #36 月末自检 — `monthly_summary.py`

**触发**: 每月最后一日 21:00 定时任务 (Agent 帮配)。

**Agent 责任**:
1. 定时触发后, 读 `alerts.md`
2. 主动推: "本月 87 笔, 支出 ¥8,200 / 收入 ¥15,000, 储蓄率 45%, 比上月 +5pp"
3. 月初 (1 号) 也跑一次 (补上月末没跑的情况), 覆盖范围: 上月整月
4. 用户说"3 月花了多少" → 调脚本 `--month 2026-03`

**脚本做什么**:
- 范围: 当月 1 号 ~ 当月最后一天
- 输出: 笔数 / 支出 / 收入 / 储蓄率 / 分类汇总 / 跨账户流量
- 写到 `alerts.md`

**边界**:
- ❌ 不做预算建议 ("下月应该少花 10%")
- ✅ 给数据

**失败兜底**:
- `--month` 指定月份无交易 → 仍输出空月报
- 当月未结束 → 截止到今日 (不报错)

### L. #38 默认账户解析 — `scripts/transaction_create.py` + `config/default_accounts.yaml` + `scripts/lib/learning_tracker.py`

**触发**: 用户说"午餐沙县 45 元"但**没指定账户**;或说"还款" / "地铁" / "加油" 等带语义线索的输入。

**Agent 责任**:
1. **首次 Onboarding 步骤 3 扩展** (V1.3.3): 把 12 条 `config/default_accounts.yaml` 规则告诉用户: "我默认这样配: 还款→CMB 储蓄卡 / 地铁公交→交通卡 / 加油→招行信用卡 / 餐饮→招商信用卡 / 高铁→招行信用卡, 同意就装, 想改哪条?"
2. **记账时自动选账户**: 调 `scripts/transaction_create.py` 时不传 `--account` 也不在 note 里写明, 走 5 层解析: `user > note > config > learning > fallback` (优先级从高到低)
3. **第一次静默记录**: learning.json 累加 count (不打扰用户)
4. **第二次跟第一次不同就询问** (`ask_on_2nd`): "你这次 地铁 早高峰 用 交通卡, 但之前 地铁 类都是用 CMB (1 次), 改默认吗? [改 / 保持 / 都不"
5. **学习只按 "类别 + 关键词" 粒度** (不按粗 category): `extract_keywords` 提取 2-4 字中文片段, "地铁早高峰" 跟 "地铁晚高峰" 算两个独立 rule

**脚本做什么**:
- `default_account_resolver.py` 5 层解析: 用户显式 `--account` > note 里 `账户:招商` 字样 > config 12 条 regex 规则 > learning.json 历史偏好 > fallback (最常用的账户)
- `learning_tracker.py` 累加 count + 处理 ask_on_2nd + 写回 learning.json
- `transaction_create.py` 写 expense/income 文件到 `Transactions/{type}/{out,in}/YYYY-MM-DD-{account}-{category}-{amount}.md`

**边界**:
- ❌ 不要自动调 `installment_helper` 创建分期组 (那是用户显式说"分期"才调)
- ❌ transfer 类型**必须同时写 out + in 两个文件** (V1.3.3 修复: 之前只写一个, 配对校验会失败)
- ✅ learning 只在用户同意后才覆盖 config (默认 ask 一次)

**失败兜底**:
- vault 没 `config/default_accounts.yaml` → INFO 提示用户跑 `bash install.sh` 或手动 `cp config/default_accounts.yaml ~/Obsidian/finance/`
- 同名文件已存在 → 走 `ask_message` soft alert, 保留旧文件, 不强制覆盖 (按 AGENTS.md 偏好: "文件保留, agent 询问 fix/ignore/delete")
- `--account` 账户名不在 `account-list.md` → ERROR, 不静默 fallback (会污染学习)

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

- **V1.2.1** (2026-06-02) — 修复 aweskill 不同步 scripts/ 的问题: Onboarding 步骤 3 新增"安装/验证 scripts/" 强制步骤 (Agent 主动帮用户 clone 仓库或 cp 脚本), 步骤 5 加 8:10 loan_payment_reminder, README 顶部加"📦 安装"段说明两种方式
- **V1.2** (2026-06-02) — 新增 #37 贷款账户 (loan type, 4 字段: 贷款总额/月供/剩余期数/起始月) + loan_payment_reminder.py 月供提醒 + monthly_summary.py 加"贷款账户进度"段 + check_negative_balances 豁免 loan/credit-card
- **V1.1** (2026-06-02) — 新增 6 个主动行为 (#23 信用卡 / #24 分期 / #33 频率 / #34 账户遗忘 / #35 周末复盘 / #36 月末自检), 升级 Onboarding 步骤 4 为 5 个定时任务
- **V1.0** (2026-06-01) — 初版, 定义 Agent 主动行为原则
