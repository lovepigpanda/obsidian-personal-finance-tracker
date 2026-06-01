---
title: Expense Category Rules — Expense Category Auto-Mapping
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: category-rules
tags: [finance, category-rules, expense]
description: Expense keyword → category auto-mapping rules, called by Templater template
---

# Expense Category Auto-Mapping Rules

> This file defines keyword → category mapping. When using Templater template for entry, it auto-suggests the corresponding category based on the note content entered by the user.

## Mapping Rules (KEY → VALUE)

| # | Keywords (match if contains any) | Category | Note |
|---|----------------------------------|----------|------|
| 1 | lunch, dinner, breakfast, takeout, restaurant, food, meal, snack, Shaxian, Lanzhou, fast food, canteen, early breakfast, midnight snack, BBQ, hotpot, 午餐, 晚餐, 早餐, 外卖, 餐厅, 吃饭, 沙县, 兰州 | Food | Food & dining |
| 2 | subway, bus, taxi, uber, parking, gas, train, travel, DiDi, hitchhike, cycling, 地铁, 公交, 打车, 滴滴, 停车, 加油 | Transport | Transportation |
| 3 | Taobao, JD, Pinduoduo, shopping, clothes, shoes, supermarket, daily goods, store, electronics, phone, 淘宝, 京东, 拼多多, 购物, 超市, 衣服 | Shopping | Shopping & consumption |
| 4 | movie, game, music, video, iQIYI, Tencent Video, Steam, Netflix, subscription, KTV, 电影, 游戏, 音乐, 视频, 会员, Steam | Entertainment | Entertainment & leisure |
| 5 | hospital, pharmacy, medicine, checkup, dental, TCM, clinic, medical, see doctor, registration, 医院, 药店, 体检, 牙科, 门诊 | Health | Healthcare |
| 6 | course, tuition, book, training, exam, subscription, edu, learning, tutorial, extracurricular, 课程, 学费, 书籍, 培训, 考试, 订阅 | Education | Education & learning |
| 7 | rent, property, utilities, gas, repair, furniture, renovation, housekeeping, cleaning, 房租, 物业, 水电, 燃气, 维修, 家居 | Housing | Housing & living |
| 8 | phone, mobile plan, broadband, data, communication, landline, 手机, 话费, 宽带, 流量, 通讯 | Communication | Communication |
| 9 | red envelope, gift, treat,人情, gift giving, 份子钱, 红包, 礼物, 请客 | Gift | Gifts & social |
| 10 | flight, hotel, travel, ticket, vacation, sightseeing, scenic spot, 机票, 酒店, 旅游, 门票, 旅行 | Travel | Travel & trips |
| 11 |理财, fund, stock, investment, loss, 理财, 基金, 股票, 投资, 亏损 | Investment | Investment |
| 12 | other, miscellaneous, 其他, 杂项 | Other | Other |

---

## Usage

1. **Templater template call**: In `expense-template.md`, the Templater script reads this file's content and matches keywords based on note input to return the corresponding category.

2. **Match priority**: Matches top-to-bottom by row number; stops at first match (so precise keywords come first, broad keywords last).

3. **Multi-keyword support**: Each category supports multiple keywords separated by `,`; matches if input contains any keyword.

4. **No match**: If note contains no keywords, template prompts user to manually select category.

---

## How to Add/Modify Rules

1. Add new row at end of table
2. Use next sequential number
3. Separate keywords with `,` (no spaces)
4. To adjust priority, move entire row to target position

---

## Category Reference (Full List)

| Category | Emoji |
|----------|-------|
| Food | 🍔 |
| Transport | 🚌 |
| Shopping | 🛍️ |
| Entertainment | 🎮 |
| Health | 💊 |
| Education | 📚 |
| Housing | 🏠 |
| Communication | 📱 |
| Gift | 🎁 |
| Travel | ✈️ |
| Investment | 💹 |
| Other | ❓ |

---

> Related: [[Expense Categories]] · [[Income Category Rules]] · [[Finance Dashboard]]