---
title: Transfer Categories — 转账分类定义
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: category-list
tags: [finance, categories, transfer]
---

## 转账分类列表

| 分类 | 英文名 | Emoji | 说明 |
|------|--------|-------|------|
| 转账 | Transfer | 🔁 | 账户间资金转移（不算收支） |

---

## 分类关键词映射规则

| 关键词 | 映射分类 |
|--------|---------|
| 转账, 转给, 打给, 转入, 转出, 转到, 来自, 调拨, 调头寸, 还信用卡, 还卡, 补仓, 充值, 提现, from, to | Transfer |

---

## 重要说明

**转账 ≠ 收入/支出**，是账户间的资金转移。

**存储方式：双文件配对**
- 转出文件：`Transactions/transfers/out/{date}-transfer-out-{from}-to-{to}-{amount}-{CCY}-ACTIVE.md`
- 转入文件：`Transactions/transfers/in/{date}-transfer-in-{to}-from-{from}-{amount}-{CCY}-ACTIVE.md`
- 配对 ID：两个文件用相同的 `transfer_pair_id` 关联

**账户余额计算逻辑：**
- 转出账户：初始余额 + 收入 − 支出 − 转出
- 转入账户：初始余额 + 收入 − 支出 + 转入
- 转账不计入"总支出"或"总收入"

**多币种转账：**
- 转出和转入默认同币种
- 跨币种转账需在外层标注汇率（如 1000 USD → 7200 CNY），但 Dataview 仍按各自币种统计

---

## 自定义分类方法

转账只有一个分类（Transfer），无需扩展。如需区分调拨目的（还卡/补仓/周转发工资），用 `note` 字段记录即可。

> 关联：[[Finance Dashboard]] · [[Expense Categories]] · [[Income Categories]]
