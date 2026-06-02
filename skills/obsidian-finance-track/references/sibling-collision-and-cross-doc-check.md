# 多 agent 共享 repo 工作协议

本文档归档本项目 (`obsidian-personal-finance-tracker`) 多 agent 并行写文件时的**三个新坑**——`patch` 工具的 sibling 警告处理 + commit 前跨文档一致性检查 + integration test 最小 fixture 模板。

继承 [patch-tool-pitfalls.md](./patch-tool-pitfalls.md) 和 [v1-proactive-features.md](./v1-proactive-features.md) 的上下文, 本节不重复讲 replace_all / 跨月算法 / vault 路径等已归档的坑。

---

## 坑 F: `patch` 工具的 sibling-collision 警告

**触发条件**: 同一 repo 里有多个 agent / subagent 在并行 patch 同一文件。Hermes `patch` 工具会发出警告:

```
_warning: /path/to/file.md was modified by sibling subagent '20260601_230334_09fb1e'
          but this agent never read it. Read the file before writing to avoid
          overwriting the sibling's changes.
```

**正确处理流程** (3 步, 总耗时 ~3 秒):

1. **`pgrep` 验证 sibling 是否还活着**:
   ```bash
   pgrep -af "claude|codex|hermes|openclaw" | head -10
   ```
   - **0 命中** → sibling 已结束, 警告是历史提醒, 直接 patch
   - **有命中** → sibling 活跃, **停下来**先确认: sibling 改的是哪一段? 你的 patch 会不会踩到? 必要时用 `git diff <file>` 看 sibling 的 latest 改动

2. **如果 sibling 死了但警告响了**: 直接 patch。理由: 警告是 cache 检查 (你本 turn 没读该文件), 不是真正的并发冲突检测

3. **如果 sibling 活着**: 先 `git diff <file>` 看清 sibling 的最新改动, 决定:
   - 你要改的区域 sibling 没碰 → patch 安全
   - sibling 改的就是你要改的 → **别 patch**, 改用 read_file + write_file 整文件重写, 或等 sibling 结束

**反例**: 看到警告就放弃 patch, 转而 `read_file` + 整文件 `write_file` —— 会丢掉 sibling 改过的内容。

**验证**: patch 成功后 `git diff <file>` 只显示你预期的改动, 没有 sibling 的内容被覆盖。

### Sibling ID 跟踪模板

每个 turn 记录 sibling 状态, 写进本 session 的 todo/笔记:

```
sibling 20260601_222012_08bff9: 2026-06-01 22:20 last activity → 已结束 (~24h)
sibling 20260601_230334_09fb1e: 新出现 → 改过 README.md, 30+ 分钟无活动
```

`08bff9` vs `09fb1e` 是**两个不同的 sibling**。新 sibling 出现不一定意味着老 sibling 重启 —— 可能是接力。

---

## 坑 G: commit 前必须做跨文档 grep 同步检查

**问题** (本 session 真实事故): 改了 `zh/AGENTS-PROACTIVE.md` 写 "每日 8:00 跑 credit_card_reminder", 但 `README.md` 表格里 sibling 写的还是 "每日 09:00"——`commit` 前 `git status` 没显示, 4 个文件 diff 也只关注本 session 改的。最后是 `git diff README.md | head -40` 时**偶然**发现。

**根因**: 项目是 4 文档中英双语同步 (`zh/AGENTS-PROACTIVE.md`, `en/AGENTS-PROACTIVE.md`, `README.md`, `skills/.../SKILL.md` + `SKILL_en.md`), **任何一个**数值 (时间 / 阈值 / 公式) 都要在 4 处保持一致。改一处后, **剩下 3 处必须 grep 同步**。

### 检查清单 (commit 前必跑, 30 秒)

```bash
# 模式: 找所有包含特定数值的文档
grep -n "8:00\|9:00\|09:00\|18:00" \
  README.md \
  zh/AGENTS-PROACTIVE.md \
  en/AGENTS-PROACTIVE.md \
  skills/obsidian-finance-track/SKILL.md \
  skills/obsidian-finance-track/SKILL_en.md
```

**判定标准**:

| 模式 | 出现位置 | 期望值 |
|------|---------|--------|
| 信用卡 reminder 时间 | 表格 + 用法块 | 全部 8:00 |
| daily check 时间 | 表格 + 步骤 4 | 全部 18:00 |
| 周复盘时间 | 表格 + 步骤 4 | 全部 20:00 (周末) |
| 阈值 (#33) | daily check 描述 | 全部 7 天 |
| 阈值 (#34) | daily check 描述 | 全部 14 天 |
| 储蓄率公式 | monthly_summary 描述 | 全部 `(收入-支出)/收入` |

**如果有不一致**: **修文档统一到代码** —— 不要反过来改代码 (用户会感知到 6 个脚本运行行为变化, 但不会去仔细读 4 份文档)。

### 哪些数值要 grep

按本项目经验, 4 类:

1. **时间** (cron 表达式 / 时分)
2. **阈值** (天数 / 笔数 / 百分比)
3. **字段名** (`statement_day` vs `账单日` / `transfer_pair_id` vs `配对 ID`)
4. **命令路径** (脚本相对路径 `scripts/xxx.py` vs 绝对路径)

### 自动化建议 (TODO, 未实施)

写一个 `scripts/check_doc_consistency.py`, 接受 `(key, value, files)` 三元组, grep 全部 files 看 value 是否一致, 不一致就 exit 1 + 列出冲突。commit 前 hook 跑。

---

## 坑 H: integration test 最小 fixture 模板

[v1-proactive-features.md 坑 E](./v1-proactive-features.md#坑-e-测试-vault-不能用---vault-) 说了 "用 `/tmp/test-vault/` 模拟真实结构", 但没说**最小要放什么文件**。本 session 验证过的最小 fixture (7 个 md, 覆盖 6 脚本全部正向路径):

```
/tmp/finance-test-vault/
├── Accounts/
│   └── account-list.md        # 至少 1 cash + 1 credit-card (带 statement_day/payment_due_day) + 1 savings
└── Transactions/
    ├── expenses/
    │   ├── 2026-05-30-lunch.md       # 7 天内正常支出, 触发 #33 "近期有记账" 正常路径
    │   ├── 2026-06-01-mbp-1.md       # 分期首期, installment_group_id + installment_index=1
    │   └── 2026-05-15-old.md        # 16+ 天前支出, 触发 #34 闲置检测
    ├── incomes/
    │   └── 2026-06-01-salary.md      # 收入, 触发 weekly/monthly 收入聚合
    └── transfers/
        ├── out/2026-06-01-to-savings.md   # transfer_pair_id 配对
        └── in/2026-06-01-from-cmb.md      # 同 pair_id
```

### frontmatter 必填字段 (按脚本)

| 脚本 | 必填 | 测试场景 |
|------|------|---------|
| daily_integrity | `date, type, amount, currency, account / from_account / to_account, status`, transfer_pair_id (transfer only) | 透支 / 配对 / 闲置 |
| credit_card_reminder | account-list: `type=credit-card`, 账单日, 还款日 | 距离下次出账日 < 5 天 WARN |
| installment_check | `installment_group_id, installment_total, installment_index` | 只有 1/12 期 → 缺 N-1 期 WARN |
| weekly_summary | `date` 在本周内, `type, amount, currency, account` | 至少 1 笔收支 |
| monthly_summary | `date` 在本月内, `type, amount` | 储蓄率公式正确 |

### Trick

如果只是想测 "脚本不崩", 上面 7 个文件已足够。**不要**复制整个项目仓库当 test-vault —— 会跑出 N 笔真实交易污染 alerts.md。

**清理**: `rm -rf /tmp/finance-test-vault/` (一次性, 不留)。

### 跑测试的标准顺序

1. 准备 fixture (上面的 7 个 md)
2. `daily_integrity_check` (1 个最关键的脚本, 验证基线)
3. `credit_card_reminder` (验证 B 类功能 schema)
4. `installment_check` (验证 schema + 完整性)
5. `installment_helper create --first-file <首期> --total 12` (验证 N-1 PENDING 生成)
6. `weekly_summary` + `monthly_summary` (验证聚合 + 储蓄率公式)

每个脚本预期至少 1 个 WARN/INFO (说明 trigger 了真路径), 0 个 ERROR (说明没崩)。

---

## 🎯 本节 vs 既有 reference 的关系

| 文件 | 关注 |
|------|------|
| [v1-proactive-features.md](./v1-proactive-features.md) | 6 个新功能设计 + 坑 A-E (跨月算法, 分期 bug, 列名匹配, INFO 误判, vault 路径) |
| [patch-tool-pitfalls.md](./patch-tool-pitfalls.md) | replace_all 灾难恢复 + 5 项自检 |
| **本文件** | 坑 F (sibling warning) + 坑 G (跨文档 grep) + 坑 H (fixture 模板) |

**核心差异**: 本文件是**多 agent 并行 + commit 流程**的协议, 前两个是**单 agent 写代码 / 写文档**的协议。
