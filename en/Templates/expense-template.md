---
title: Expense Template — Templater Interactive Entry (Auto Category Mapping)
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: template
tags: [template, expense, finance]
description: Templater interactive template with auto-read category-rules for keyword → category mapping
---

<%*
// ========== Expense Entry Template (Auto Category Mapping) ==========
// Function: Interactive expense entry with note keyword → category auto-mapping

// 1. Read category rules file
const rulesPath = "Categories/expense-category-rules.md";
const rulesContent = await tp.file.find_tfile(rulesPath) 
  ? await app.vault.read(await app.vault.getAbstractFileByPath(rulesPath))
  : "";

// 2. Parse mapping rules (extract KEY → VALUE from expense-category-rules.md)
const categoryMap = {};
if (rulesContent) {
  const lines = rulesContent.split("\n");
  let currentCategory = "";
  for (const line of lines) {
    // Skip header rows or separator rows
    if (line.match(/^\|.*Category.*\|/) || line.match(/^\|[\s\-:|]+$/) || line.match(/^#|^>|^##/)) continue;
    // Match table data rows
    const match = line.match(/^\|\s*[^|\s]+\s*\|([^\|]+)\|[^\|]+\|/);
    if (match) {
      const keywords = match[1].trim().split(/,\s*/).filter(k => k.length > 0);
      const category = line.match(/^\|\s*[^|\s]+\s*\|[^\|]+\|([^\|]+)\|/)?.[1]?.trim() || "";
      for (const kw of keywords) {
        categoryMap[kw] = category;
      }
    }
  }
}

// 3. Interactive input
const title = await tp.system.prompt("Expense description (e.g.: lunch, subway, shopping)");
const date = tp.date.now("YYYY-MM-DD");
const amount = await tp.system.prompt("Amount (number, e.g.: 45)");
const currency = await tp.system.suggester(["CNY", "USD", "EUR", "JPY", "HKD"], ["CNY", "USD", "EUR", "JPY", "HKD"]);
const note = await tp.system.prompt("Note (enter keywords, system auto-recommends category)\n e.g.: lunch, subway, Taobao", "");
const account = await tp.system.suggester(["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"], ["Cash", "Alipay", "WeChat Pay", "CMB", "ICBC", "Credit Card", "USD Account"]);
const payment_method = await tp.system.suggester(["Cash", "Alipay", "WeChat Pay", "Bank Transfer", "Credit Card", "Debit Card"], ["Cash", "Alipay", "WeChat Pay", "Bank Transfer", "Credit Card", "Debit Card"]);

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

// 5. If matched, offer suggestion; otherwise let user manually select
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
  // Confirm if accept recommended category
  const accept = await tp.system.suggester([
    `✅ ${finalCategory} (auto-recommended)`, "❌ Manual select"
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

// 6. Build filename and save path
const fileName = `${date}-${title}-${amount}-${currency}-ACTIVE.md`;
const filePath = `Transactions/expenses/${fileName}`;

// 7. Move file to target path
await tp.file.move(filePath);

// 8. Output completion info
-%>

✅ Expense recorded: `Transactions/expenses/<% fileName %>`
- Category: <% finalCategory %>
- Amount: <% amount %> <% currency %>
- Account: <% account %>

> To edit, open the file and modify frontmatter, or view [[Finance Dashboard]] for summary