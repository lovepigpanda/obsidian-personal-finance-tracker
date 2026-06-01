---
title: Expense Categories — 支出分类定义
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: category-list
tags: [finance, categories, expense]
---

## 支出分类列表

| 分类 | 英文名 | Emoji | 说明 |
|------|--------|-------|------|
| 餐饮 | Food | 🍔 | 餐厅、外卖、快餐、小吃 |
| 交通 | Transport | 🚌 | 地铁、公交、打车、停车、加油 |
| 购物 | Shopping | 🛍️ | 淘宝、京东、拼多多、超市、衣服 |
| 娱乐 | Entertainment | 🎮 | 电影、游戏、音乐、视频平台订阅 |
| 医疗 | Health | 💊 | 医院、药店、体检、牙科 |
| 教育 | Education | 📚 | 课程、书籍、培训、考试 |
| 居住 | Housing | 🏠 | 房租、物业、水电、燃气、维修 |
| 通讯 | Communication | 📱 | 手机话费、宽带、流量 |
| 礼物 | Gift | 🎁 | 红包、礼物、请客、人情 |
| 旅游 | Travel | ✈️ | 机票、酒店、旅游、门票 |
| 投资 | Investment | 💹 | 理财、基金、股票（支出） |
| 其他 | Other | ❓ | 其他杂项支出 |

---

## 分类关键词映射规则

> 以下规则供 Templater 模板自动映射使用。当用户在 note 字段输入包含左侧关键词时，系统自动 suggest 对应分类。

| 关键词 | 映射分类 |
|--------|---------|
| 午餐, 晚餐, 早餐, 外卖, 餐厅, 吃饭, 餐饮, 沙县, 兰州, 快餐, 食堂 | Food |
| 地铁, 公交, 打车, taxi, uber, 停车, 加油, 高铁, 火车, 出行 | Transport |
| 淘宝, 京东, 拼多多, 购物, 衣服, 鞋子, 超市, 日用品 | Shopping |
| 电影, 游戏, 音乐, 视频, 爱奇艺, 腾讯视频, steam, 奈飞, 会员 | Entertainment |
| 医院, 药店, 买药, 体检, 牙科, 中医, 门诊 | Health |
| 课程, 学费, 书籍, 培训, 考试, 订阅, edu | Education |
| 房租, 物业, 水电, 燃气, 维修, 家居 | Housing |
| 手机, 话费, 宽带, 流量, 通讯 | Communication |
| 红包, 礼物, 请客, 人情, 送礼物 | Gift |
| 机票, 酒店, 旅游, 门票, 旅行, 度假 | Travel |
| 理财, 基金, 股票（支出） | Investment |
| 其他, 杂项 | Other |

---

## 自定义分类方法

如需添加/修改分类：
1. 在上方表格中添加新分类行
2. 在映射规则中添加关键词 → 分类映射
3. Templater 模板会自动读取这些规则

> 关联：[[Finance Dashboard]] · [[Income Categories]]