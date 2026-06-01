---
title: Transfer Template — Templater Interactive Transfer Entry (Paired Dual Files)
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: template
tags: [template, transfer, finance]
description: Templater interactive template, creates 2 paired files in one go (transfer-out + transfer-in), linked by transfer_pair_id
---

<%*
// ========== 转账录入模板（双文件配对）==========
// 一次创建 2 个 .md 文件：out + in，用 transfer_pair_id 关联
// 账户余额计算：转出账户 = 初始 + income - expense - transfer_out
//              转入账户 = 初始 + income - expense + transfer_in

const accounts = ["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account", "HK Account", "建行", "工商银行"];

// 1. 交互式输入
const title = await tp.system.prompt("Transfer description (e.g., credit card payment, top-up, position adjustment)");
const date = tp.date.now("YYYY-MM-DD");
const amount = await tp.system.prompt("Amount (number, e.g., 5000)");
const currency = await tp.system.suggester(["CNY", "USD", "EUR", "JPY", "HKD"], ["CNY", "USD", "EUR", "JPY", "HKD"]);
const from_account = await tp.system.suggester(accounts, accounts);
const to_account = await tp.system.suggester(accounts.filter(a => a !== from_account), accounts.filter(a => a !== from_account));
const note = await tp.system.prompt("Note (optional, e.g., credit card payment, emergency transfer)", "");
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

| Field | Value |
|------|-------|
| **Type** | Transfer |
| **Direction** | Pair ID: \`${pair_id}\` |
| **From account** | ${from_account} |
| **To account** | ${to_account} |
| **Amount** | ${amount} ${currency} |
| **Note** | ${note || "—"} |
| **Status** | ACTIVE |

> Paired file: search \`transfer_pair_id: ${pair_id}\` to find the counterpart
> Related: [[Finance Dashboard]] · [[Account List]]
`;

const outFileName = `${date}-transfer-out-${from_account}-to-${to_account}-${amount}-${currency}-ACTIVE.md`;
const inFileName = `${date}-transfer-in-${to_account}-from-${from_account}-${amount}-${currency}-ACTIVE.md`;

await app.vault.create(`Transactions/transfers/out/${outFileName}`, baseFrontmatter);
await app.vault.create(`Transactions/transfers/in/${inFileName}`, baseFrontmatter);
-%>

✅ Transfer paired records created:
- Transfer-out: `Transactions/transfers/out/<% outFileName %>`
- Transfer-in: `Transactions/transfers/in/<% inFileName %>`
- Pair ID: `<% pair_id %>`
- From account: <% from_account %>
- To account: <% to_account %>
- Amount: <% amount %> <% currency %>

> To find the pair: search `transfer_pair_id: <% pair_id %>` to find the counterpart
> Related: [[Finance Dashboard]] · [[Account List]]
