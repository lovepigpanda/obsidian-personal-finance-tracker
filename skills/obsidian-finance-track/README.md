# Skill Installation Guide

## 🤖 AI Agent Skill: obsidian-finance-track

This folder contains the **AI Agent Skill** for Obsidian personal finance tracking.

---

## What's Included

```
skills/obsidian-finance-track/
├── SKILL.md       # 中文版 Skill 定义（主要）
├── SKILL_en.md    # English version
└── README.md      # 本文件
```

---

## How to Use This Skill

### For Hermes Agent Users

**Option 1: Use from GitHub project directly**
```bash
# Clone the project
git clone https://github.com/lovepigpanda/obsidian-personal-finance-tracker.git ~/Project/obsidian-personal-finance-tracker

# Create symlink to skills folder
ln -s ~/Project/obsidian-personal-finance-tracker/skills/obsidian-finance-track ~/.hermes/skills/obsidian-finance-track
```

**Option 2: Copy the skill folder**
```bash
# Copy to Hermes skills directory
cp -r ~/Project/obsidian-personal-finance-tracker/skills/obsidian-finance-track ~/.hermes/skills/
```

**Option 3: Install via aweskill** (if you have SkillClaw)
```bash
aweskill install https://github.com/lovepigpanda/obsidian-personal-finance-tracker/tree/main/skills/obsidian-finance-track
```

### For Other AI Agents (Claude, etc.)

The `SKILL.md` file contains the complete workflow. You can:

1. Read `SKILL.md` directly to understand the accounting workflow
2. Reference `zh/AGENTS.md` and `zh/QUICK-REFERENCE.md` for full details
3. Copy the relevant parts into your agent's system prompt

---

## Skill Features

- ✅ **Natural language parsing** — "今天午餐沙县花了45元" → transaction file
- ✅ **Auto category mapping** — keywords → 12 expense / 7 income categories
- ✅ **Multi-currency** — CNY / USD / EUR / JPY / HKD
- ✅ **Multi-account** — Alipay / WeChat Pay / CMB / ICBC / Credit Card / Cash
- ✅ **Auto file creation** — creates properly formatted .md files
- ✅ **Dataview dashboard** — auto-updates financial overview

---

## Skill Triggers

Loaded when user says anything like:
- 记账、记一笔、花了、买了、支出、收入、收到
- expense、income、spent、paid、received、salary
- 支付宝、微信支付、红包、余额

---

## File Structure

```
obsidian-personal-finance-tracker/     ← GitHub project (the source of truth)
├── zh/                                 ← Chinese version (primary)
│   ├── AGENTS.md                      ← AI Agent workflow guide
│   ├── QUICK-REFERENCE.md             ← Category/account mapping tables
│   ├── Templates/                     ← Templater templates
│   ├── Transactions/                  ← Transaction .md files
│   ├── Dashboards/                    ← Dataview dashboards
│   ├── Accounts/                      ← Account definitions
│   └── Categories/                   ← Category rules
├── en/                                 ← English version
└── skills/
    └── obsidian-finance-track/        ← 🤖 AI Agent Skill
        ├── SKILL.md                   ← Skill definition (Chinese)
        ├── SKILL_en.md                ← Skill definition (English)
        └── README.md                  ← This file
```

---

## More Info

- **Project**: https://github.com/lovepigpanda/obsidian-personal-finance-tracker
- **Skill Version**: V1.0
- **License**: MIT