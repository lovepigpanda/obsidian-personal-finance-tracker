# Hermes patch 工具使用规范 + 灾难恢复

本文档归档 Hermes `patch` 工具的**安全使用模式**和**replace_all 误用恢复流程**。适用于所有涉及 README/CHANGELOG/SKILL.md 等"重复结构多"文件的项目。

---

## ⚠️ 头号铁律: 不要在短字符串上用 replace_all

**问题场景** (2026-06-01 obsidian-finance-track README 事故):

```python
# ❌ 错误: 在 README.md 多处出现的 `weekly_dashboard_check.py` (出现 4+ 次) 上用 replace_all=True
patch(mode='replace', path='README.md', old_string='# 周度结构\n.../weekly_dashboard_check.py\n```',
      new_string='# 周度结构\n.../weekly_dashboard_check.py\n\n+新增 weekly_summary.py 段\n```',
      replace_all=True)  # ← 灾难! 替换所有 4+ 处, README 整页污染
```

**为什么 disaster**: 短字符串 + `replace_all=True` 会匹配**所有**出现位置, 即使你想只改某一段。

**正确做法** (3 种, 按优先级):

1. **在 old_string 中加唯一上下文**, 让匹配只剩 1 处:
   ```python
   # 包含 5-10 行上下文, 例如: 上一个段落标题 + 中间内容 + 目标行
   old_string = '''# 周度结构
   python3 .../weekly_dashboard_check.py
   ```
   
   ### 通知渠道'''
   ```

2. **不用 replace_all, 分次 patch** (即使要做 5 次也值得)

3. **如果一定要用 replace_all, 用长字符串** (≥ 50 字符), 让它天然只匹配 1 处

---

## 🚨 误用后的恢复流程

### 情况 1: 文件还没 commit

```bash
cd /path/to/repo
git checkout -- <污染文件>
# 重新精确做 patch (用唯一上下文)
```

### 情况 2: 文件已 commit

```bash
cd /path/to/repo
# 选项 A: revert commit (最干净, 不丢其他改动)
git revert HEAD~1  # 或具体的 commit SHA

# 选项 B: 改完后 amend (如果污染在 HEAD commit)
# 选项 C: 如果只想撤销 README 部分, 用 git restore --staged + git restore + 重做
git restore README.md  # 回到 HEAD 版本
# 重新精确做 patch
```

### 情况 3: 文件已 push 到 GitHub

```bash
# 不要 force push! 用 git revert (产生新 commit 撤销, 历史可追溯)
git revert <bad_commit_sha>
git push
```

---

## ✅ patch 工具调用前自检清单

每次调 patch 前, **5 秒检查**这 4 项:

| # | 检查项 | 通过条件 |
|---|--------|---------|
| 1 | old_string ≥ 5 行 (含上下文) | 是 |
| 2 | 整个 old_string 在文件内**只出现 1 次** | 是 (用 `grep -c` 验证) |
| 3 | 没设 `replace_all=True` (除非 old_string ≥ 50 字符且只匹配 1 处) | 是 |
| 4 | new_string 的格式 (缩进/换行) 跟上下文一致 | 是 |

**强制预检命令** (调 patch 前必跑):

```bash
# 验证 old_string 只出现 1 次
grep -c "<old_string 第一行>" path/to/file.md
# 输出必须是 1, 否则加更多上下文
```

---

## 📋 跟 patch 工具配合的常用 grep 模式

```bash
# 找某段标题 (用于 patch 前的导航)
grep -n "^## " path/to/file.md

# 找某脚本/函数的所有出现位置 (避免 replace_all 灾难)
grep -n "weekly_dashboard_check" path/to/file.md

# 检查 patch 后改动量
git diff --stat path/to/file.md

# 验证 patch 没破坏文件 (Markdown 不报错, 但 Python/YAML 会)
python3 -c "import yaml; yaml.safe_load(open('file.yml'))"
```

---

## 🔄 关联教训: 不对称的"重做 vs 撤销"成本

| 场景 | 撤销成本 | 重做成本 | 应该选 |
|------|---------|---------|--------|
| 改 1 行文字 (对错难分) | 低 | 低 | 直接改 |
| 改 10 行函数 (语义可能错) | 中 | 中 | 用 patch 调, 失败就 revert |
| 改 100 行 README 模板 | **极高** (要重新精修) | **极高** | 必用唯一上下文, **永远不用 replace_all 短串** |
| 改 schema/数据格式 (影响所有下游) | 极高 | 极高 | 先写测试, 再改代码 |

**经验法则**: 改动越大, 越要花时间加 unique context 防止误替换。

---

## 🎯 适用场景

- 任何**会用到 patch 工具**的 Agent session
- 任何**需要修改 README/CHANGELOG/SKILL.md 重复结构**的任务
- 任何**跨多个文件做对称改动**的批量操作 (考虑 git grep + xargs 替代 patch)
