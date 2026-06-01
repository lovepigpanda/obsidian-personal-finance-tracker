---
title: Expense Template — Templater 交互录入支出（含自动分类映射）
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: template
tags: [template, expense, finance]
description: Templater 交互模板，自动读取 category-rules 实现备注关键词 → 分类自动映射
---

<%*
// ========== 支出录入模板（自动分类映射版）==========
// 功能：交互式录入支出，自动根据 note 关键词映射分类

// 1. 读取分类规则文件
const rulesPath = "Categories/expense-category-rules.md";
const rulesContent = await tp.file.find_tfile(rulesPath) 
  ? await app.vault.read(await app.vault.getAbstractFileByPath(rulesPath))
  : "";

// 2. 解析映射规则（从 expense-category-rules.md 提取 KEY → VALUE 映射）
const categoryMap = {};
if (rulesContent) {
  const lines = rulesContent.split("\n");
  let currentCategory = "";
  for (const line of lines) {
    // 匹配表头行或分隔符行，跳过
    if (line.match(/^\|.*序号.*\|/) || line.match(/^\|[\s\-:|]+$/) || line.match(/^#|^>|^##/)) continue;
    // 匹配表格数据行
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
const title = await tp.system.prompt("支出描述（如：lunch, subway, shopping）");
const date = tp.date.now("YYYY-MM-DD");
const amount = await tp.system.prompt("金额（数字，如：45）");
const currency = await tp.system.suggester(["CNY", "USD", "EUR", "JPY", "HKD"], ["CNY", "USD", "EUR", "JPY", "HKD"]);
const note = await tp.system.prompt("备注（输入关键词，系统自动推荐分类）\n例如：午餐、地铁、淘宝", "");
const account = await tp.system.suggester(["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"], ["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"]);
const payment_method = await tp.system.suggester(["Cash", "Alipay", "WeChat Pay", "Bank Transfer", "Credit Card", "Debit Card"], ["Cash", "Alipay", "WeChat Pay", "Bank Transfer", "Credit Card", "Debit Card"]);

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

// 5. 如果匹配到，提供建议；否则让用户手动选择
let finalCategory = suggestedCategory;
if (!finalCategory) {
  finalCategory = await tp.system.suggester([
    "Food 🍔", "Transport 🚌", "Shopping 🛍️", "Entertainment 🎮", 
    "Health 💊", "Education 📚", "Housing 🏠", "Communication 📱", 
    "Gift 🎁", "Travel ✈️", "Investment 💹", "Other ❓"
  ], [
    "Food", "Transport", "Shopping", "Entertainment", 
    "Health", "Education", "Housing", "Communication", 
    "Gift", "Travel", "Investment", "Other"
  ]);
} else {
  // 确认是否接受推荐分类
  const accept = await tp.system.suggester([
    `✅ ${finalCategory}（自动推荐）`, "❌ 手动选择"
  ], [finalCategory, "MANUAL"]);
  if (accept === "MANUAL") {
    finalCategory = await tp.system.suggester([
      "Food 🍔", "Transport 🚌", "Shopping 🛍️", "Entertainment 🎮", 
      "Health 💊", "Education 📚", "Housing 🏠", "Communication 📱", 
      "Gift 🎁", "Travel ✈️", "Investment 💹", "Other ❓"
    ], [
      "Food", "Transport", "Shopping", "Entertainment", 
      "Health", "Education", "Housing", "Communication", 
      "Gift", "Travel", "Investment", "Other"
    ]);
  }
}

// 6. 构建文件名和保存路径
const fileName = `${date}-${title}-${amount}-${currency}-ACTIVE.md`;
const filePath = `Transactions/expenses/${fileName}`;

// 7. 移动文件到目标路径
await tp.file.move(filePath);

// 8. 输出完成信息
-%>

✅ 支出记录已创建：`Transactions/expenses/<% fileName %>`
- 分类：<% finalCategory %>
- 金额：<% amount %> <% currency %>
- 账户：<% account %>

> 如需修改，前往文件编辑 frontmatter 或 [[Finance Dashboard]] 查看汇总