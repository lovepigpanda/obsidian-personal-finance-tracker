---
title: Income Template — Templater 交互录入收入（含自动分类映射）
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: template
tags: [template, income, finance]
description: Templater 交互模板，自动读取 income-category-rules 实现备注关键词 → 分类自动映射
---

<%*
// ========== 收入录入模板（自动分类映射版）==========

// 1. 读取分类规则文件
const rulesPath = "Categories/income-category-rules.md";
const rulesContent = await tp.file.find_tfile(rulesPath)
  ? await app.vault.read(await app.vault.getAbstractFileByPath(rulesPath))
  : "";

// 2. 解析映射规则
const categoryMap = {};
if (rulesContent) {
  const lines = rulesContent.split("\n");
  for (const line of lines) {
    if (line.match(/^\|.*序号.*\|/) || line.match(/^\|[\s\-:|]+$/) || line.match(/^#|^>|^##/)) continue;
    const match = line.match(/^\|\s*\d+\s*\|([^\|]+)\|([^\|]+)\|/);
    if (match) {
      const keywords = match[1].trim().split(/,\s*/).filter(k => k.length > 0);
      const category = match[2].trim();
      for (const kw of keywords) {
        categoryMap[kw] = category;
      }
    }
  }
}

// 3. 交互式输入
const title = await tp.system.prompt("收入描述（如：salary, bonus, freelance）");
const date = tp.date.now("YYYY-MM-DD");
const amount = await tp.system.prompt("金额（数字，如：15000）");
const currency = await tp.system.suggester(["CNY", "USD", "EUR", "JPY", "HKD"], ["CNY", "USD", "EUR", "JPY", "HKD"]);
const note = await tp.system.prompt("备注（输入关键词，系统自动推荐分类）\n例如：工资、年终奖、兼职", "");
const account = await tp.system.suggester(["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"], ["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"]);

// 4. 自动分类映射
let suggestedCategory = "";
if (note && Object.keys(categoryMap).length > 0) {
  for (const [keyword, category] of Object.entries(categoryMap)) {
    if (note.includes(keyword)) {
      suggestedCategory = category;
      break;
    }
  }
}

let finalCategory = suggestedCategory;
if (!finalCategory) {
  finalCategory = await tp.system.suggester([
    "Salary 💰", "Bonus 🎉", "Freelance 💻", "Investment 📈", "Refund 🔄", "Gift 🎁", "Other ❓"
  ], [
    "Salary", "Bonus", "Freelance", "Investment", "Refund", "Gift", "Other"
  ]);
} else {
  const accept = await tp.system.suggester([
    `✅ ${finalCategory}（自动推荐）`, "❌ 手动选择"
  ], [finalCategory, "MANUAL"]);
  if (accept === "MANUAL") {
    finalCategory = await tp.system.suggester([
      "Salary 💰", "Bonus 🎉", "Freelance 💻", "Investment 📈", "Refund 🔄", "Gift 🎁", "Other ❓"
    ], [
      "Salary", "Bonus", "Freelance", "Investment", "Refund", "Gift", "Other"
    ]);
  }
}

// 5. 构建文件名和保存路径
const fileName = `${date}-${title}-${amount}-${currency}-ACTIVE.md`;
const filePath = `Transactions/incomes/${fileName}`;

await tp.file.move(filePath);
-%>

✅ 收入记录已创建：`Transactions/incomes/<% fileName %>`
- 分类：<% finalCategory %>
- 金额：<% amount %> <% currency %>
- 账户：<% account %>

> 如需修改，前往文件编辑 frontmatter 或 [[Finance Dashboard]] 查看汇总