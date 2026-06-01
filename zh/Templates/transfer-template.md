---
title: Transfer Template — Templater 交互录入转账（双文件配对）
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: template
tags: [template, transfer, finance]
description: Templater 交互模板，一次创建 2 个配对文件（转出 + 转入），用 transfer_pair_id 关联
---

<%*
// ========== 转账录入模板（双文件配对）==========
// 一次创建 2 个 .md 文件：out + in，用 transfer_pair_id 关联
// 账户余额计算：转出账户 = 初始 + income - expense - transfer_out
//              转入账户 = 初始 + income - expense + transfer_in

const accounts = ["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account", "HK Account", "建行", "工商银行"];

// 1. 交互式输入
const title = await tp.system.prompt("转账描述（如：还信用卡、补仓、调头寸）");
const date = tp.date.now("YYYY-MM-DD");
const amount = await tp.system.prompt("金额（数字，如：5000）");
const currency = await tp.system.suggester(["CNY", "USD", "EUR", "JPY", "HKD"], ["CNY", "USD", "EUR", "JPY", "HKD"]);
const from_account = await tp.system.suggester(accounts, accounts);
const to_account = await tp.system.suggester(accounts.filter(a => a !== from_account), accounts.filter(a => a !== from_account));
const note = await tp.system.prompt("备注（可选，如：还信用卡、应急周转）", "");
const pair_id = `T-${date}-${Date.now().toString(36)}`;

// 2. 构建两个文件内容
const baseFrontmatter = `---
type: transfer
date: ${date}
amount: ${amount}
currency: ${currency}
category: Transfer
from_account: ${from_account}
to_account: ${to_account}
transfer_pair_id: ${pair_id}
note: "${note}"
tags: [transfer, finance]
status: ACTIVE
created: ${date}
---

# ${date} — Transfer: ${from_account} → ${to_account}

| 字段 | 值 |
|------|-----|
| **类型** | 转账 |
| **方向** | 配对 ID：\`${pair_id}\` |
| **转出账户** | ${from_account} |
| **转入账户** | ${to_account} |
| **金额** | ${amount} ${currency} |
| **备注** | ${note || "—"} |
| **状态** | ACTIVE |

> 配对文件：搜索 \`transfer_pair_id: ${pair_id}\` 找到对端
> 关联：[[Finance Dashboard]] · [[Account List]]
`;

const outFileName = `${date}-transfer-out-${from_account}-to-${to_account}-${amount}-${currency}-ACTIVE.md`;
const inFileName = `${date}-transfer-in-${to_account}-from-${from_account}-${amount}-${currency}-ACTIVE.md`;

await app.vault.create(`Transactions/transfers/out/${outFileName}`, baseFrontmatter);
await app.vault.create(`Transactions/transfers/in/${inFileName}`, baseFrontmatter);
-%>

✅ 转账配对记录已创建：
- 转出：`Transactions/transfers/out/<% outFileName %>`
- 转入：`Transactions/transfers/in/<% inFileName %>`
- 配对 ID：`<% pair_id %>`
- 转出账户：<% from_account %>
- 转入账户：<% to_account %>
- 金额：<% amount %> <% currency %>

> 查询配对：搜索 `transfer_pair_id: <% pair_id %>` 可找到对端
> 关联：[[Finance Dashboard]] · [[Account List]]
