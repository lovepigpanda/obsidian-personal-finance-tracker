---
title: Account List — 账户列表
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: account-list
tags: [finance, accounts]
---

## 账户定义

> 账户余额由 `scripts/daily_integrity_check.py` 每日预计算, 写入 `Accounts/balances.md` 快照, Dataview 只读快照 (性能 O(1))。初始余额需在下方表格手动设置。

| 账户名 | 类型 | 币种 | 初始余额 | 账单日 | 还款日 | 贷款总额 | 月供 | 月供日 | 合同总期数 | 剩余期数 | 起始月 | 说明 | 状态 |
|--------|------|------|---------|--------|--------|---------|------|--------|---------|---------|--------|------|------|
| Cash | cash | CNY | 0 | - | - | - | - | - | - | - | - | 现金 | ACTIVE |
| Alipay | e-wallet | CNY | 0 | - | - | - | - | - | - | - | - | 支付宝 | ACTIVE |
| WeChat Pay | e-wallet | CNY | 0 | - | - | - | - | - | - | - | - | 微信支付 | ACTIVE |
| CMB | bank | CNY | 0 | - | - | - | - | - | - | - | - | 招商银行 | ACTIVE |
| ICBC | bank | CNY | 0 | - | - | - | - | - | - | - | - | 工商银行 | ACTIVE |
| Credit Card | credit-card | CNY | 0 | 5 | 25 | - | - | - | - | - | - | 信用卡（负数表示负债） | ACTIVE |
| USD Account | bank | USD | 0 | - | - | - | - | - | - | - | - | 美元账户 | ACTIVE |
| Mortage | loan | CNY | -1000000 | - | - | 1000000 | 8500 | 31 | 240 | 240 | 2024-01 | 房贷示例：30 年, 月供日 31 (1月有, 2/4/6/9/11 自动用 30/28), 总期数 240 | ACTIVE |

> **信用卡说明**：账单日是出账日，还款日是最后还款日（如出账后 20 天）。`#23` 主动提醒依赖这两个字段。
> 信用卡示例（CMB 招行）：账单日 5 号，还款日 25 号。
> 添加信用卡账户时，**必须**填账单日 + 还款日，否则不会提醒。

> **贷款说明**：贷款账户用 6 个结构化字段描述。
>
> 必填 5 个 (脚本才能算月供提醒):
> 1. **贷款总额** (`Principal`) - float
> 2. **月供** (`Monthly Payment`) - float
> 3. **月供日** (`Payment Day`) - 1-31, 真实扣款日 (不是写死的"月末", 脚本会按当月实际天数自动处理, 2 月自动 28/29)
> 4. **合同总期数** (`Total Months` / `贷款期数`) - int
> 5. **起始月** (`Start Month`) - YYYY-MM 格式
>
> 可选 1 个 (用于一致性校验):
> 6. **剩余期数** (`Remaining Months`) - int
>
> `#37` 贷款月供提醒依赖这 5-6 个字段。**未填全 = 不会提醒** (只报 INFO 字段缺失)。
>
> 还月供 = 写一条 expense 交易 (`account=贷款账户名`, `amount=月供`)。脚本扫当月 expense 自动判断"已还"。
> 跟信用卡一样的逻辑, 不需要专门 tracking 字段。
>
> 一致性校验 (如果填了剩余期数): 已还期数 (从 expense 推) + 剩余期数 == 合同总期数, 不等时报 WARN 提示数据 stale。
>
> 简化处理: 如果 `payment_day=31` 在 4/6/9/11 月只有 30 天, 自动用 30; 2 月只有 28/29 天, 自动用月末。无需用户手动处理。
>
> 添加贷款账户时, **必须**填 5 个必填字段, 否则 `#37` 不会提醒 (只会 INFO 报缺失)。

---

## 账户余额实时计算

> ✅ 此处由 Dataview 读 `Accounts/balances.md` 快照(由 `scripts/daily_integrity_check.py` 每日写入)。
>
> 不再每次打开都全扫描 Transactions/ — 性能 O(1),数据量 10w 笔也不卡。
>
> 余额算法: `initial_balance + sum(income) - sum(expense) - sum(transfer-out) + sum(transfer-in)`,见 `scripts/lib/balance.py`。
> 强制刷新: `python3 scripts/daily_integrity_check.py`

```dataview
table account as "账户", currency as "币种", balance as "当前余额"
from "Accounts"
where type = "balance-snapshot"
flatten balances
sort account asc
```

---

## 添加新账户

1. 在上方表格中添加一行，填写账户信息
2. 将新账户名添加到初始余额映射中
3. 在 Templater 模板的 account 选项中也会自动出现

> 关联：[[Finance Dashboard]] · [[Expense Categories]] · [[Income Categories]]