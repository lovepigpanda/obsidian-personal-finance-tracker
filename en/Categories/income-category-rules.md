---
title: Income Category Rules — Income Category Auto-Mapping
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: category-rules
tags: [finance, category-rules, income]
description: Income keyword → category auto-mapping rules, called by Templater template
---

# Income Category Auto-Mapping Rules

> This file defines keyword → category mapping for income. When using Templater template for income entry, it auto-suggests the corresponding category based on the note content entered by the user.

## Mapping Rules (KEY → VALUE)

| # | Keywords (match if contains any) | Category | Note |
|---|----------------------------------|----------|------|
| 1 | salary, wages, base pay, paycheck, 工资, 月薪, 薪资, 底薪, 发工资, 工资到账 | Salary | Employment income |
| 2 | year-end bonus, bonus, performance, dividend, 年终奖, 奖金, 绩效, 分红, 年奖, 季度奖 | Bonus | Performance bonuses |
| 3 | freelance, side job, gig, contract work,自由职业, 兼职, 外快, 接单, 私活 | Freelance | Freelance income |
| 4 | investment interest, fund dividend, stock gain, dividend,理财利息, 投资收益, 基金分红, 股票收益 | Investment | Investment returns |
| 5 | refund, return, compensation, 赔偿, 退款, 退货, 补偿 | Refund | Refunds & compensation |
| 6 | red envelope, gift money, 红包, 礼金 | Gift | Gift money |
| 7 | other, incidental income, 其他, 偶然收入 | Other | Other income |

---

## Usage

1. **Templater template call**: In `income-template.md`, the Templater script reads this file's content and matches keywords based on note input to return the corresponding category.

2. **Match priority**: Matches top-to-bottom by row number; stops at first match.

3. **Multi-keyword support**: Each category supports multiple keywords separated by `,`; matches if input contains any keyword.

4. **No match**: If note contains no keywords, template prompts user to manually select category.

---

## Category Reference (Full List)

| Category | Emoji |
|----------|-------|
| Salary | 💰 |
| Bonus | 🎉 |
| Freelance | 💻 |
| Investment | 📈 |
| Refund | 🔄 |
| Gift | 🎁 |
| Other | ❓ |

---

> Related: [[Income Categories]] · [[Expense Category Rules]] · [[Finance Dashboard]]