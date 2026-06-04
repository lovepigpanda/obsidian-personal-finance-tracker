#!/usr/bin/env bash
# install.sh — 一键初始化账本 vault (V1.3.3+ #38 + V1.4 --install-plist)
#
# 作用: 把仓库的 templates/categories/dashboards/accounts/config/scripts 复制到 vault
#       + 可选安装 7 段 plist 到 ~/Library/LaunchAgents/ (V1.4+)
#
# 用法:
#   bash install.sh [VAULT_PATH]                       # 基础 vault 初始化
#   bash install.sh --dry-run [VAULT_PATH]             # dry-run, 只 echo
#   bash install.sh --en [VAULT_PATH]                  # 英文模板
#   bash install.sh --install-plist [--vault PATH]     # 装 7 段 launchd plist
#   bash install.sh --uninstall-plist                  # 卸载 plist
#   bash install.sh --install-plist --dry-run          # dry-run plist
#
# 行为:
#   - 已存在的文件**保留** (不覆盖, 防止破坏用户历史数据)
#   - 缺失的文件从仓库 cp 过去
#   - plist 装到 ~/Library/LaunchAgents/ + launchctl load -w
#   - 全部 dry-run-able: bash install.sh --dry-run
#
# 设计: 按用户偏好"soft alert" — 文件保留, agent 询问 fix/ignore/delete, 不强制覆盖
#
# V1.4 新增 (Evan 2026-06 反馈, finance-install-sh-add-install-plist P1):
#   - 修 V1.1.4-V1.3.3 4 个版本空头支票: SKILL.md 说"必须真交付 plist"但 install.sh 没实现
#   - 加 --install-plist / --uninstall-plist 真装
#   - 7 段 (跟 SKILL.md 247/293-300 行硬要求对齐, todo note 漏列 weekly_dashboard_check 修正)
#   - 显式 --vault flag (V1.3.3 旧版用 positional, 加 flag 后会冲突)
#   - 短路: --install-plist/--uninstall-plist 模式跳过 vault 初始化

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
VAULT="$HOME/Obsidian/finance"
DRY_RUN=false
LANG_CHOICE="zh"
INSTALL_PLIST=false
UNINSTALL_PLIST=false
VAULT_SET=false

# 2-pass 解析: 找 --vault 拿下一个 arg, 第一个非 flag 当 vault (V1.3.3 兼容)
i=0
args=("$@")
while [ $i -lt $# ]; do
  arg="${args[$i]}"
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --en) LANG_CHOICE="en" ;;
    --install-plist) INSTALL_PLIST=true ;;
    --uninstall-plist) UNINSTALL_PLIST=true ;;
    --vault=*) VAULT="${arg#--vault=}"; VAULT_SET=true ;;
    --vault) i=$((i+1)); VAULT="${args[$i]:-}"; VAULT_SET=true ;;
    -*) ;;  # 跳过其他 flag
    *)
      # positional: V1.3.3 兼容, 第一个非 flag 当 vault
      if [ "$VAULT_SET" = false ]; then
        VAULT="$arg"
        VAULT_SET=true
      fi
      ;;
  esac
  i=$((i+1))
done

echo "=== install.sh V1.4 ==="
echo "  仓库根: $REPO_ROOT"
echo "  Vault:   $VAULT"
echo "  语言:    $LANG_CHOICE"
echo "  Dry-run: $DRY_RUN"
echo "  Install-plist: $INSTALL_PLIST"
echo "  Uninstall-plist: $UNINSTALL_PLIST"
echo

# ============================================================================
# V1.4: --install-plist / --uninstall-plist 模式短路 vault 初始化
# ============================================================================
# 设计: 这两个模式是 V1.4 新增, 用户可能只想装/卸 plist, 不需要再跑一遍
#       vault mkdir + cp 模板。所以 plist 段在最前面, exit 0 退出, 不走到 vault 段
if $INSTALL_PLIST; then
  echo "=== 安装 7 段 plist (V1.4+ 必备) ==="
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PYTHON_BIN="/usr/bin/python3"

  if ! $DRY_RUN; then
    mkdir -p "$PLIST_DIR"
  fi

  # V1.4 路径策略: 优先用主仓 ~/Project/obsidian-personal-finance-tracker/,
  # 不存在才 fallback 到 $REPO_ROOT (从当前目录跑的情况)
  # 原因: SKILL.md 模板 (312 行) 期望 plist 指向主仓路径; 用户升级主仓 (git pull)
  #       时, plist 仍能找到脚本; 而 $REPO_ROOT 可能是 aweskill 装的临时副本
  PREFERRED_REPO="$HOME/Project/obsidian-personal-finance-tracker"
  if [ -d "$PREFERRED_REPO/scripts" ]; then
    SCRIPTS_ROOT="$PREFERRED_REPO/scripts"
    echo "  使用主仓路径: $SCRIPTS_ROOT (主仓升级 git pull 不会断 plist)"
  else
    SCRIPTS_ROOT="$REPO_ROOT/scripts"
    echo "  [WARN] 主仓 $PREFERRED_REPO 不存在, fallback 到: $SCRIPTS_ROOT"
  fi

  install_one_plist() {
    local label="$1"
    local script_name="$2"
    local hour="$3"
    local minute="$4"
    local weekday="${5:-}"      # 可选: 0=周日
    local day="${6:-}"          # 可选: 1-31 (月最后一日用 Day 31 + launchd 自动跳过不存在日期)

    local script_path="$SCRIPTS_ROOT/${script_name}"
    local plist_path="$PLIST_DIR/${label}.plist"

    # 校验脚本存在 (dry-run 模式跳过这步)
    if ! $DRY_RUN && [ ! -f "$script_path" ]; then
      echo "  [ERR]  $label: 脚本不存在 $script_path"
      return 1
    fi

    # 构造 StartCalendarInterval dict
    local interval="            <key>Hour</key><integer>${hour}</integer>
            <key>Minute</key><integer>${minute}</integer>"
    if [ -n "$weekday" ]; then
      interval="${interval}
            <key>Weekday</key><integer>${weekday}</integer>"
    fi
    if [ -n "$day" ]; then
      interval="${interval}
            <key>Day</key><integer>${day}</integer>"
    fi

    local plist_content="<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
    <key>Label</key>
    <string>${label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_BIN}</string>
        <string>${script_path}</string>
        <string>--vault</string>
        <string>${VAULT}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
${interval}
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/finance-${label#com.finance.}.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/finance-${label#com.finance.}.err.log</string>
</dict>
</plist>
"

    if $DRY_RUN; then
      echo "  [DRY]  写 $plist_path"
      echo "  [DRY]  launchctl load -w $plist_path"
      return 0
    fi

    # 写 plist
    echo "$plist_content" > "$plist_path"
    echo "  [NEW]  $plist_path"

    # launchctl load -w (立即 load + 写盘, 重启也保持)
    if launchctl load -w "$plist_path" 2>/dev/null; then
      echo "  [LOAD] $label"
    else
      # load 失败可能因为已 load, 先 unload 再 load
      launchctl unload "$plist_path" 2>/dev/null || true
      if launchctl load -w "$plist_path" 2>/dev/null; then
        echo "  [RELOAD] $label"
      else
        echo "  [ERR]  load 失败: $label (plist 语法检查 plutil -lint $plist_path)"
        return 1
      fi
    fi
  }

  # 7 段 plist (按 SKILL.md 247/293-300 行的硬要求, todo note 漏列 weekly_dashboard_check 修正)
  # 注意: 脚本真实文件名是下划线 `daily_integrity_check.py` (仓库内是这个名字)
  #       SKILL.md 模板里 V1.3.3 写成空格 `daily integrity_check.py` 是拼写错, V1.4 install.sh 修
  install_one_plist "com.finance.daily-integrity"        "daily_integrity_check.py"      18  0
  install_one_plist "com.finance.credit-card-reminder"   "credit_card_reminder.py"        8  0
  install_one_plist "com.finance.installment-check"      "installment_check.py"           8  5
  install_one_plist "com.finance.loan-payment-reminder"  "loan_payment_reminder.py"       8 10
  install_one_plist "com.finance.weekly-dashboard-check" "weekly_dashboard_check.py"     8  0 0   # 每周日 08:00 (Weekday=0)
  install_one_plist "com.finance.weekly-summary"         "weekly_summary.py"             20  0 0   # 每周日 20:00 (Weekday=0)
  install_one_plist "com.finance.monthly-summary"        "monthly_summary.py"            21  0 "" 31  # 每月最后一日 21:00 (Day=31, launchd 自动跳过不存在日期)

  echo
  if $DRY_RUN; then
    echo "=== install-plist dry-run 完成 (7 段都 dry-run, 没真装) ==="
  else
    echo "=== install-plist 完成 ==="
    echo
    echo "验证 (应该看到 7 行 com.finance.*):"
    echo "  launchctl list | grep com.finance"
  fi
  exit 0
fi

if $UNINSTALL_PLIST; then
  echo "=== 卸载 7 段 plist ==="
  PLIST_DIR="$HOME/Library/LaunchAgents"
  for label in \
    "com.finance.daily-integrity" \
    "com.finance.credit-card-reminder" \
    "com.finance.installment-check" \
    "com.finance.loan-payment-reminder" \
    "com.finance.weekly-dashboard-check" \
    "com.finance.weekly-summary" \
    "com.finance.monthly-summary"; do
    plist="$PLIST_DIR/${label}.plist"
    if [ -f "$plist" ]; then
      if $DRY_RUN; then
        echo "  [DRY] launchctl unload $plist"
        echo "  [DRY] rm $plist"
      else
        launchctl unload "$plist" 2>/dev/null && echo "  [UNLOAD] $label" || echo "  [WARN] unload 失败 (可能没在跑): $label"
        rm "$plist" && echo "  [REMOVED] $plist" || echo "  [ERR] 删除失败: $plist"
      fi
    else
      echo "  [SKIP] $plist (不存在)"
    fi
  done
  echo "=== uninstall-plist 完成 ==="
  exit 0
fi

# ============================================================================
# V1.3.3 vault 初始化段 (默认行为, 无 flag 时跑)
# ============================================================================

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
echo "  3. 跑 'bash install.sh --install-plist' 装 7 段 launchd 定时任务 (V1.4+, 取代旧'配 launchd / cron')"
