---
title: Income Template — Templater Interactive Entry (Auto Category Mapping)
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: template
tags: [template, income, finance]
description: Templater interactive template with auto-read income-category-rules for keyword → category mapping
---

<%*
// ========== Income Entry Template (Auto Category Mapping) ==========

// 1. Read category rules file
const rulesPath = "Categories/income-category-rules.md";
const rulesContent = await tp.file.find_tfile(rulesPath)
  ? await app.vault.read(await app.vault.getAbstractFileByPath(rulesPath))
  : "";

// 2. Parse mapping rules
const categoryMap = {};
if (rulesContent) {
  const lines = rulesContent.split("\n");
  for (const line of lines) {
    if (line.match(/^\|.*Category.*\|/) || line.match(/^\|[\s\-:|]+$/) || line.match(/^#|^>|^##/)) continue;
    const match = line.match(/^\|\s*[^|\s]+\s*\|([^\|]+)\|([^\|]+)\|/);
    if (match) {
      const keywords = match[1].trim().split(/,\s*/).filter(k => k.length > 0);
      const category = match[2].trim();
      for (const kw of keywords) {
        categoryMap[kw] = category;
      }
    }
  }
}

// 3. Interactive input
const title = await tp.system.prompt("Income description (e.g.: salary, bonus, freelance)");
const date = tp.date.now("YYYY-MM-DD");
const amount = await tp.system.prompt("Amount (number, e.g.: 15000)");
const currency = await tp.system.suggester(["CNY", "USD", "EUR", "JPY", "HKD"], ["CNY", "USD", "EUR", "JPY", "HKD"]);
const note = await tp.system.prompt("Note (enter keywords, system auto-recommends category)\n e.g.: salary, year-end bonus, freelance", "");
const account = await tp.system.suggester(["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"], ["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"]);

// 4. Auto category mapping
let suggestedCategory = "";
if (note && Object.keys(categoryMap).length > 0) {
  for (const [keyword, category] of Object.entries(categoryMap)) {
    if (note.toLowerCase().includes(keyword.toLowerCase())) {
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
    `✅ ${finalCategory} (auto-recommended)`, "❌ Manual select"
  ], [finalCategory, "MANUAL"]);
  if (accept === "MANUAL") {
    finalCategory = await tp.system.suggester([
      "Salary 💰", "Bonus 🎉", "Freelance 💻", "Investment 📈", "Refund 🔄", "Gift 🎁", "Other ❓"
    ], [
      "Salary", "Bonus", "Freelance", "Investment", "Refund", "Gift", "Other"
    ]);
  }
}

// 5. Build filename and save path
const fileName = `${date}-${title}-${amount}-${currency}-ACTIVE.md`;
const filePath = `Transactions/incomes/${fileName}`;

await tp.file.move(filePath);
-%>

✅ Income recorded: `Transactions/incomes/<% fileName %>`
- Category: <% finalCategory %>
- Amount: <% amount %> <% currency %>
- Account: <% account %>

> To edit, open the file and modify frontmatter, or view [[Finance Dashboard]] for summary