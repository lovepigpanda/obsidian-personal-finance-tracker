#!/usr/bin/env bash
# install.sh — 一键初始化账本 vault (V1.3.3+ #38)
#
# 作用: 把仓库的 templates/categories/dashboards/accounts/config/scripts 复制到 vault
# 用法: bash install.sh [VAULT_PATH]
#   默认 VAULT_PATH = ~/Obsidian/finance
#
# 行为:
#   - 已存在的文件**保留** (不覆盖, 防止破坏用户历史数据)
#   - 缺失的文件从仓库 cp 过去
#   - 全部 dry-run-able: bash install.sh --dry-run
#
# 设计: 按用户偏好"soft alert" — 文件保留, agent 询问 fix/ignore/delete, 不强制覆盖

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
VAULT="${1:-$HOME/Obsidian/finance}"
DRY_RUN=false
LANG_CHOICE="zh"

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --en) LANG_CHOICE="en" ;;
  esac
done

echo "=== install.sh V1.3.3 ==="
echo "  仓库根: $REPO_ROOT"
echo "  Vault:   $VAULT"
echo "  语言:    $LANG_CHOICE"
echo "  Dry-run: $DRY_RUN"
echo

# 1. 创建 vault 目录结构
VAULT_DIRS=(
  "Templates"
  "Categories"
  "Dashboards"
  "Accounts"
  "Transactions/expenses/out"
  "Transactions/expenses/in"
  "Transactions/incomes/out"
  "Transactions/incomes/in"
  "Transactions/transfers/out"
  "Transactions/transfers/in"
  "Daily"
  "Reports"
  "Scripts"
)
for d in "${VAULT_DIRS[@]}"; do
  target="$VAULT/$d"
  if [ -d "$target" ]; then
    echo "  [OK]   $d/"
  else
    if $DRY_RUN; then
      echo "  [DRY]  mkdir -p $d/"
    else
      mkdir -p "$target"
      echo "  [NEW]  $d/"
    fi
  fi
done

echo

# 2. 复制文件 (存在跳过, 缺失补)
copy_file() {
  local src="$1"
  local dest="$2"
  if [ ! -f "$src" ]; then
    echo "  [SKIP] $src (源文件不存在)"
    return
  fi
  if [ -f "$dest" ]; then
    echo "  [KEEP] $dest (已存在, 保留)"
  else
    if $DRY_RUN; then
      echo "  [DRY]  cp $src $dest"
    else
      cp "$src" "$dest"
      echo "  [NEW]  $dest"
    fi
  fi
}

echo "--- Templates ---"
for f in "$REPO_ROOT/$LANG_CHOICE/Templates/"*.md; do
  copy_file "$f" "$VAULT/Templates/$(basename "$f")"
done

echo
echo "--- Categories ---"
for f in "$REPO_ROOT/$LANG_CHOICE/Categories/"*.md; do
  copy_file "$f" "$VAULT/Categories/$(basename "$f")"
done

echo
echo "--- Dashboards ---"
for f in "$REPO_ROOT/$LANG_CHOICE/Dashboards/"*.md; do
  copy_file "$f" "$VAULT/Dashboards/$(basename "$f")"
done

echo
echo "--- Accounts ---"
for f in "$REPO_ROOT/$LANG_CHOICE/Accounts/"*.md; do
  copy_file "$f" "$VAULT/Accounts/$(basename "$f")"
done

echo
echo "--- Config (V1.3.3+ #38) ---"
copy_file "$REPO_ROOT/config/default_accounts.yaml" "$VAULT/default_accounts.yaml"

echo
echo "--- Scripts (仓库 → vault) ---"
# 复制 scripts/ 到 vault/Scripts/ 让用户本地也能跑 (无需 ~/Project/... 绝对路径)
for f in "$REPO_ROOT/scripts/"*.py; do
  copy_file "$f" "$VAULT/Scripts/$(basename "$f")"
done
for f in "$REPO_ROOT/scripts/lib/"*.py; do
  if [[ "$(basename "$f")" == "__init__.py" ]] || [[ "$(basename "$f")" == "__pycache__" ]]; then continue; fi
  copy_file "$f" "$VAULT/Scripts/lib/$(basename "$f")"
done

echo
echo "=== install.sh 完成 ==="
echo
echo "下一步:"
echo "  1. 编辑 ~/Obsidian/finance/Accounts/account-list.md — 填你的账户 + 初始余额"
echo "  2. 调 Agent 让它跑 Onboarding 7 步"
echo "  3. 配 launchd / cron 定时任务 (见 zh/AGENTS-PROACTIVE.md 步骤 4)"
