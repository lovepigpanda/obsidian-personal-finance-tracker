---
title: Income Category Rules — 收入分类自动映射规则
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: category-rules
tags: [finance, category-rules, income]
description: 收入关键词 → 分类 自动映射规则，供 Templater 模板调用
---

# 收入分类自动映射规则

> 本文件定义关键词到分类的映射关系。

## 映射规则

| 序号 | 关键词（包含任一即匹配） | 映射分类 | 说明 |
|------|-------------------------|---------|------|
| 1 | 工资, 月薪, 薪资, 底薪, 发工资, 工资到账, 工资发放 | Salary | 工资收入 |
| 2 | 年终奖, 奖金, 绩效, 分红, 年奖, 季度奖, 项目奖金 | Bonus | 奖金收入 |
| 3 | 兼职, 外快, 接单, 私活, 自由职业, freelance, 接活 | Freelance | 兼职外快 |
| 4 | 理财, 利息, 投资收益, 基金分红, 股票收益, 股息, 分红 | Investment | 投资理财收益 |
| 5 | 退款, 退货, 补偿, 赔偿, 赔付 | Refund | 退款补偿 |
| 6 | 红包, 礼金 | Gift | 礼金红包 |
| 7 | 其他, 偶然收入 | Other | 其他收入 |

---

## 分类参考

| 分类 | 英文 | Emoji |
|------|------|-------|
| 工资 | Salary | 💰 |
| 奖金 | Bonus | 🎉 |
| 兼职 | Freelance | 💻 |
| 理财收益 | Investment | 📈 |
| 退款 | Refund | 🔄 |
| 礼金 | Gift | 🎁 |
| 其他 | Other | ❓ |

---

> 关联：[[Income Categories]] · [[Expense Category Rules]] · [[Finance Dashboard]]