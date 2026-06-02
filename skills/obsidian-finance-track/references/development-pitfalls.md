# Development Pitfalls — Lessons from Real Updates

Each pitfall below was hit during a real session and resolved. Future agents editing this skill or its scripts should expect to encounter them again.

---

## Pitfall 1: macOS Case-Insensitive Filesystem Trap

**Symptom**: `git status` reports a brand-new `Scripts/` (capital S) as untracked, but you created `scripts/` (lowercase). Or: `mkdir -p scripts/...` creates `Scripts/` instead.

**Cause**: macOS HFS+/APFS is **case-insensitive but case-preserving** by default. When `Scripts/` already exists (perhaps from a prior `mkdir` that got autocapitalized), creating `scripts/` is a no-op (they're the same folder). Worse: git sees them as two distinct paths.

**Fix recipe**:
```bash
# 1. Try the rename
mv Scripts scripts 2>&1
# On case-insensitive FS, this fails with "same file" — need 2-step:
mv Scripts _Scripts_temp && mv _Scripts_temp scripts
```

**Prevention**:
- Always use the exact casing from the first `mkdir`. Pick lowercase, stick with it.
- For distributed projects, **always use lowercase** for tooling directories (`scripts/`, `lib/`, `bin/`, `docs/`).
- If a user reports "git says Scripts/ is untracked but I created scripts/", this is why.

---

## Pitfall 2: `.gitignore` with `*.md` Blocks Core Assets

**Symptom**: After `git add .`, none of the new `.md` files in `Templates/`, `Categories/`, `Dashboards/`, etc. get staged. `git status --ignored` shows them as ignored. `git ls-files` confirms the older `.md` files (added before the `*.md` rule) are tracked, but new ones aren't.

**Cause**: The project had `.gitignore` containing `*.md` to keep personal ledger data out of git. But this also silently ignores all **distributable** `.md` assets (Templates, Categories, AGENTS.md, etc.).

**Fix recipe**:
```gitignore
# ❌ WRONG — too broad, blocks core assets
*.md

# ✅ RIGHT — explicit paths only
zh/Transactions/
en/Transactions/
Transactions/

# Plus any other dirs that hold user-private data
```

**Verification after fix**:
```bash
git status --ignored   # should now show .md files as untracked (not ignored)
git ls-files | wc -l  # should match what you intend to ship
```

**Prevention**:
- Never use extension-based ignore (`*.md`, `*.json`, `*.yaml`) in projects where that extension is a core asset type.
- Use **path-based** ignore (`dir/`, `dir/**`) for content you want to keep private.
- After editing `.gitignore`, run `git status --ignored` to verify the change did what you wanted.

---

## Pitfall 3: Transfer `from_account` / `to_account` Semantics — Pick ONE

**Symptom**: Validation script fails on every transfer pair. Error: "from/to accounts differ between out and in files". Or: example transfer files in different sessions have inconsistent from/to directions.

**Cause**: There's an unresolved design question: when a transfer is recorded as TWO files (out + in), do they share the same `from_account` / `to_account` fields, or are they mirrored?

**Two valid designs**:

| Design | out file | in file | Query impact | Balance calc impact |
|--------|----------|---------|--------------|---------------------|
| **A. Unified** (recommended) | from=A, to=B | from=A, to=B | Both files match a single `from:A to:B` query | in file adds to B (to_account) |
| **B. Mirrored** (in 视角) | from=A, to=B | from=B, to=A | Each file has its own perspective | Both files express the same physical event from opposite sides |

**The project chose Design A (Unified)**. Rationale:
- Single source of truth per transfer (one logical event, one canonical representation).
- Validator can do exact `out.from == in.from AND out.to == in.to` check.
- In-file title (e.g., "CMB ← Alipay") and "received" semantic don't conflict with frontmatter — frontmatter describes the money flow, title describes the perspective.

**Fix recipe** (if you accidentally designed B and want to switch to A):
1. Update example files: set both `from_account` and `to_account` to the **same** values in out and in files.
2. Update validation script: change from "expected_from = pfm.get('to_account')" (mirrored) to "from_acc == pfm.get('from_account')" (unified).
3. Update template comments to explain the unified semantic.
4. Document in SKILL.md "步骤 6" that both files share the same fields.

**Prevention**:
- When designing any dual-file record pattern, **decide unified vs mirrored upfront** and document it in:
  1. The data model spec
  2. The template frontmatter (with a comment)
  3. The validator (with the matching check)
  4. The example files (with the matching fields)
- The three places must be consistent. Mismatch = silent bug.
- If unsure: **pick unified**. Mirrored adds complexity for no analytical gain.

---

## Pitfall 4: Python `__pycache__/` Gets Committed If You Forget

**Symptom**: After committing scripts/, git shows `scripts/lib/__pycache__/balance.cpython-314.pyc` and friends. These are platform-specific Python bytecode files — they bloat the repo and create merge conflicts across Python versions.

**Fix recipe**:
```gitignore
__pycache__/
*.pyc
*.pyo
```
```bash
# If already committed:
git rm --cached -r scripts/lib/__pycache__/
git add .gitignore
git commit --amend --no-edit   # or new commit
```

**Prevention**: Add `__pycache__/` to `.gitignore` **at the same time** you add any `*.py` file. Don't wait until after the first commit.

---

## Pitfall 5: `baseFrontmatter` Translation Drift in Bilingual Skills

**Symptom**: A Chinese skill template has `baseFrontmatter: 类型|方向|转出账户|...`. An English version was generated by a subagent, but the **frontmatter field names inside the template string** are still in Chinese. AI Agent running in English mode reads the template and tries to fill Chinese field names.

**Cause**: Subagent translation passes copy the structure but miss strings that are *inside other strings* (the YAML template literal).

**Fix recipe**:
```bash
# After bilingual translation, search for Chinese in en/ files
grep -rP '[\x{4e00}-\x{9fff}]' en/   # any Chinese characters in en/?
# Then specifically search for content that should be translated
grep -rn "类型\|方向\|转出账户" en/  # should be 0 hits
```

**Prevention**:
- After any bilingual translation pass, run a grep for Chinese characters in `en/` and vice versa.
- The skill's `AGENTS.md` should require that **template string content** (the literal text that goes into user .md files) must match the file's language. Don't just translate the **wrapper** (the SKILL.md instructions).
- This is a sub-class of "translation validation" — always verify translations by running the localized version, not by trusting subagent reports.

---

## Cross-Cutting Lesson: Validate Subagent Reports

This session: a subagent reported "translation complete" but the `en/Templates/transfer-template.md` had Chinese characters in the `baseFrontmatter` block. The bug was only caught by manually `grep`-ing the file and reading the result.

**Rule**: When a subagent (or any non-interactive process) reports completion of translation/file-creation, **verify by reading the actual file** before committing. Don't trust the summary.

**Verification commands for bilingual content**:
```bash
# Find any Chinese in en/ (should be 0)
grep -rP '[\x{4e00}-\x{9fff}]' en/

# Find any English in zh/ (should be 0, modulo code blocks)
grep -rP '[\x{41}-\x{5a}]' zh/

# Find any untranslated section headers (look for patterns the other language uses)
# e.g. "步骤" in en/, "Step" in zh/
```

---

## Meta-Pattern: Patching Files After a Long Edit Chain

When patching a SKILL.md or any large file, the `patch` tool requires `old_string` to be unique. After 5+ patches to the same file, the file's structure has shifted, and an old `old_string` from earlier in the conversation may no longer match (whitespace, surrounding context, etc.).

**Fix**:
1. Re-read the file's current state (offset + limit) before each patch in a long session.
2. Use unique anchors: include 3-5 lines of context above/below the change.
3. If the same `old_string` appears multiple times, use `replace_all=true`.
4. If unsure, prefer `write_file` for the whole section over chained `patch` calls.

**This skill's update history demonstrates this**: 15+ patches in one session to add transfer support. Two patches accidentally removed content (示例 4 was deleted in patch #137). Recovery required reading the current state and re-inserting.

---

## Pitfall 6: README/Docs Reference Files That Don't Exist

**Symptom**: You write or rewrite a README that mentions `scripts/launchd_user.plist` or `.github/workflows/finance-check.yml` as "project ships" or "本项目自带". User follows the steps, finds the file missing, gets confused/angry.

**Why this happens**: when writing docs from a mental model of "what the project should have", it's easy to confidently assert something exists that doesn't. Especially true for setup snippets (cron, launchd, GitHub Actions) that look like boilerplate.

**Fix recipe** (after writing any README/docs):
```bash
# 1. Extract all file references from docs
grep -oE '`[^`]+\.(py|md|plist|yml|yaml|sh|json|toml)`' README.md SKILL.md | tr -d '`' | sort -u > /tmp/refs.txt

# 2. For each, check existence
while read f; do
  [ -e "$f" ] && echo "  ✓ $f" || echo "  ✗ $f (CLAIMED IN DOCS, MISSING!)"
done < /tmp/refs.txt

# 3. For commands, also check CLI exists
grep -oE 'aweskill [a-z]+ [a-z-]+' README.md | while read cmd; do
  command -v "${cmd%% *}" >/dev/null || echo "  ✗ $cmd (CLI missing)"
done
```

**When fixing a false claim**, pick the smaller of the two:
- **Option A**: Create the missing file (use a minimal stub + TODO comment)
- **Option B**: Soften the claim to "see SKILL.md for guidance" or "to be added in a future release"

Option B is usually right when the file is a deployment artifact (plist, workflow) rather than core logic.

**Prevention**:
- **After writing any README/SKILL update**, run a self-check loop that grep's every referenced path/command and verifies it exists. This takes 30 seconds and prevents user-facing 404s.
- Prefer **promising the minimum** in docs. "Read the source" > "ships with file X". Users can read source; they can't read a file that doesn't exist.
- The "保证正确" user request is a direct signal: when the user asks for completeness, they mean **correctness**, not just coverage. Pad docs with verbiage, but every line must be true.

**Real example from this session**: README claimed `scripts/launchd_user.plist` and `.github/workflows/finance-check.yml` both shipped with the project. Neither existed. User asked "保证正确" → I caught both lies → softened to "to be added in a future release" + "see SKILL.md for guidance".

---

## Pitfall 7: Docstring Lies After Code Deletion

**Symptom**: You removed a function (e.g., `send_webhook`, `_post_json`, `_http_get`) from a module but the module-level docstring at the top of the file still lists it under "支持：/Supports：" or similar "what this module does" header.

**Why this happens**: patch tool's `old_string` / `new_string` works on body code, but the top-of-file docstring is usually a separate region you don't touch when removing a function. After 2-3 rounds of "delete function, add function", the docstring drifts out of sync with reality.

**Real example from this session**: Removed all webhook code from `scripts/lib/notifier.py` (4 functions, ~70 lines, plus `import json`). The top docstring still read:
```
支持:
1. alerts.md (默认开启) - ...
2. 桌面通知 (默认开启) - ...
3. Webhook 推送 (可选) - 读环境变量，支持 Bark / PushPlus / Server酱 / 通用 webhook
```
Users reading the docstring think webhook is still supported, get a `AttributeError: module 'notifier' has no attribute 'send_webhook'` when they try.

**Fix recipe**:
1. After any non-trivial code removal, **re-read the top docstring** of the modified file. If it lists features, check each listed feature still exists.
2. If you removed functionality, update the docstring to reflect "what the module does NOW" (not what it used to do).
3. Even better: change the docstring header from "支持：/Supports：" to "支持 (基础版)/Supports (basic)：" + add a "【设计原则】" paragraph explaining what's NOT in scope and why.

**Prevention**:
- Treat the top docstring as a **contract**. When the contract changes, update it in the SAME patch as the code change.
- For skill/system modules with deliberate "we don't do X" carve-outs, make the carve-out **explicit** in the docstring so users don't ask "why doesn't this do webhook?".

**Pattern (use for any "we deliberately don't do X" module)**:
```python
"""
notifier.py - 通知分发 (基础版)

支持:
1. alerts.md (默认开启) - ...
2. 桌面通知 (默认开启) - ...

【设计原则】Webhook / 飞书 / 微信 / 邮件等通知**不**在脚本负责范围。
校验脚本只做最基础的、零配置的渠道。
其他渠道由 AI Agent 主动用自己已有的消息通道推送 (见 AGENTS-PROACTIVE.md)。
"""
```

---

## Pitfall 8: Transfer Pair Validation Fails When Both Files Have Identical Frontmatter

**Symptom**: After applying Pitfall 3's "unified semantic" fix (out and in files share the same `from_account` / `to_account`), `validate_transaction.py` STILL fails with:
```
❌ [ERROR] transfer_pair_id 'T-XXX' 找不到配对文件 (期望另一端也用相同 ID)
```
…even though both files exist and their frontmatter `transfer_pair_id` is byte-identical.

**Why this happens**: The validator might be using the **mirrored semantic** for *pair detection* (looking for `from_account == this.to_account AND to_account == this.from_account` to find the partner) but the **unified semantic** for *content check* (both files have same fields). Or vice versa. The two checks were patched at different times and are now inconsistent.

**Likely root cause** (from 2026-06 session end):
- The example files in `zh/Transactions/transfers/{out,in}/` were updated to unified semantic correctly.
- The validator's "find partner" function (probably `find_partner_by_pair_id`) may have a logic gap: it only searches one direction (e.g., scans `out/` for files with matching `transfer_pair_id` but doesn't scan `in/`).
- Or: parser returns the `from_account` value for one file but the `to_account` for the partner, then compares them — but if both are the same string, comparison says "different" due to a `set()` or `in` check that's not symmetric.

**Fix recipe** (when you hit this):
1. **Re-read the validator's source** (`scripts/validate_transaction.py`), specifically the part that says "找不到配对" / "cannot find partner".
2. Check the search: does it scan BOTH `out/` and `in/` directories? If only one, fix the search to be symmetric.
3. Check the field comparison: after unified semantic, the comparison should be `pfm.get('transfer_pair_id') == self.pfm.get('transfer_pair_id')` (just the ID match), not account-direction comparison.
4. Run the validator on a known-good pair to confirm the fix.

**Temporary debug command** (don't ship):
```python
import frontmatter, pathlib
for d in ['zh/Transactions/transfers/out', 'zh/Transactions/transfers/in']:
    for f in pathlib.Path(d).glob('*.md'):
        p = frontmatter.load(f)
        print(f, p.get('transfer_pair_id'))
```

**Prevention**:
- When changing transfer semantic (Pitfall 3's unified vs mirrored), **trace every reference** in the validator:
  1. Where the partner is found (search)
  2. How partner fields are compared (compare)
  3. How mismatches are reported (error message)
- Add a **unit test** for the validator with a known-good pair and a known-bad pair. Run it after any change.
- The pair-ID-only check is robust to semantic changes; account-direction check is fragile. Prefer the former.

**Status as of 2026-06-01 session end**: this bug surfaced right at the end of the README finalization session. NOT YET FIXED. Next session's first task should be: debug this, fix the validator, run the unit test, then commit.
