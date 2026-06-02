---
title: Account List — 账户列表
created: 2026-06-01
updated: 2026-06-01
version: V1.2
status: ACTIVE
type: account-list
tags: [finance, accounts]
---

## 账户定义

> 账户余额由 Dataview 自动计算（初始余额 + 收入 - 支出），无需手动更新。

| 账户名 | 类型 | 币种 | 初始余额 | 账单日 | 还款日 | 信用额度 | 贷款总额 | 月供 | 剩余期数 | 起始月 | 说明 | 状态 |
|--------|------|------|---------|--------|--------|---------|---------|------|---------|--------|------|------|
| Cash | cash | CNY | 0 | - | - | - | - | - | - | - | 现金 | ACTIVE |
| Alipay | e-wallet | CNY | 0 | - | - | - | - | - | - | - | 支付宝 | ACTIVE |
| WeChat Pay | e-wallet | CNY | 0 | - | - | - | - | - | - | - | 微信支付 | ACTIVE |
| CMB | bank | CNY | 0 | - | - | - | - | - | - | - | 招商银行 | ACTIVE |
| ICBC | bank | CNY | 0 | - | - | - | - | - | - | - | 工商银行 | ACTIVE |
| Credit Card | credit-card | CNY | 0 | - | - | - | - | - | - | - | 信用卡（负数表示负债） | ACTIVE |
| USD Account | bank | USD | 0 | - | - | - | - | - | - | - | 美元账户 | ACTIVE |
| Mortgage | loan | CNY | 0 | - | - | - | 1000000 | 8500 | 240 | 2024-01 | 房贷（负数=未还本金） | ACTIVE |

> **信用卡说明**：账单日是出账日，还款日是最后还款日（如出账后 20 天）。`#23` 主动提醒依赖这两个字段。
> 信用卡示例（CMB 招行）：账单日 5 号，还款日 25 号。
> 添加信用卡账户时，**必须**填账单日 + 还款日，否则不会提醒。

> **贷款账户说明**（V1.2 新增）：类型为 `loan`，余额**本应**为负数（=未还本金）。`#37` 主动提醒依赖这 4 个字段。
> 贷款账户字段说明：
> - **贷款总额 (Principal)**: 原始贷款金额
> - **月供 (Monthly Payment)**: 每月应还金额
> - **剩余期数 (Remaining Months)**: 还剩多少期
> - **起始月 (Start Month)**: YYYY-MM 格式，**第一次月供**所在月份；之后每月同日
> 还月供 = 创建一条普通 expense 交易，account=贷款账户，amount=月供即可。脚本自动检测当月是否已还、是否逾期。
> 示例（房贷）：2024-01 起始，月供 8500，剩余 240 期 → 第 1 次月供 2024-01-31，第 2 次 2024-02-29（自动处理 2 月天数），第 3 次 2024-03-31...

---

## 账户余额实时计算

> 以下由 Dataview 自动计算，每次打开文件时刷新

```dataviewjs
// 获取所有账户
const accounts = ["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"];

// 初始余额（手动维护）
const initialBalances = {
  "Cash": 0,
  "Alipay": 0,
  "WeChat Pay": 0,
  "CMB": 0,
  "ICBC": 0,
  "Credit Card": 0,
  "USD Account": 0
};

// 读取所有交易文件
const expenses = dv.pages('"Transactions/expenses"').filter(p => p.status === "ACTIVE");
const incomes = dv.pages('"Transactions/incomes"').filter(p => p.status === "ACTIVE");

// 计算每个账户余额
const results = [];
for (const account of accounts) {
  const cur = dv.current();
  const expSum = expenses.filter(p => p.account === account).amount.sum() || 0;
  const incSum = incomes.filter(p => p.account === account).amount.sum() || 0;
  const balance = (initialBalances[account] || 0) + incSum - expSum;
  results.push({ account, balance });
}

// 输出表格
dv.table(["账户", "当前余额"], results.map(r => [r.account, r.balance]));
```

---

## 添加新账户

1. 在上方表格中添加一行，填写账户信息
2. 将新账户名添加到初始余额映射中
3. 在 Templater 模板的 account 选项中也会自动出现

> 关联：[[Finance Dashboard]] · [[Expense Categories]] · [[Income Categories]]