---
title: Expense Category Rules — 支出分类自动映射规则
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: category-rules
tags: [finance, category-rules, expense]
description: 支出关键词 → 分类 自动映射规则，供 Templater 模板调用
---

# 支出分类自动映射规则

> 本文件定义关键词到分类的映射关系。Templater 模板录入时，会根据用户输入的 note 内容自动 suggest 对应分类。

## 映射规则（KEY → VALUE）

| 序号 | 关键词（包含任一即匹配） | 映射分类 | 说明 |
|------|-------------------------|---------|------|
| 1 | 午餐, 晚餐, 早餐, 外卖, 餐厅, 吃饭, 餐饮, 沙县, 兰州, 快餐, 食堂, 早点, 夜宵, 烧烤, 火锅 | Food | 餐饮相关 |
| 2 | 地铁, 公交, 打车, taxi, uber, 停车, 加油, 高铁, 火车, 出行, 滴滴, 顺风车, 骑行 | Transport | 交通出行 |
| 3 | 淘宝, 京东, 拼多多, 购物, 衣服, 鞋子, 超市, 日用品, 百货, 电器, 数码, 手机 | Shopping | 购物消费 |
| 4 | 电影, 游戏, 游戏, 音乐, 视频, 爱奇艺, 腾讯视频, steam, 奈飞, 会员, 订阅, 唱K, ktv | Entertainment | 娱乐休闲 |
| 5 | 医院, 药店, 买药, 体检, 牙科, 中医, 门诊, 医疗, 看病, 挂号 | Health | 医疗健康 |
| 6 | 课程, 学费, 书籍, 培训, 考试, 订阅, edu, 学习, 教程, 课外班 | Education | 教育学习 |
| 7 | 房租, 物业, 水电, 燃气, 维修, 家居, 装修, 家政, 保洁 | Housing | 居住相关 |
| 8 | 手机, 话费, 宽带, 流量, 通讯, 固话 | Communication | 通讯相关 |
| 9 | 红包, 礼物, 请客, 人情, 送礼物, 份子钱, 红包 | Gift | 礼物人情 |
| 10 | 机票, 酒店, 旅游, 门票, 旅行, 度假, 景区 | Travel | 旅游出行 |
| 11 | 理财, 基金, 股票, 投资, 亏损 | Investment | 投资相关 |
| 12 | 其他, 杂项 | Other | 其他 |

---

## 使用说明

1. **Templater 模板调用方式**：在 `expense-template.md` 中，Templater 脚本读取本文件内容，根据 note 输入匹配关键词，返回对应分类。

2. **匹配优先级**：按序号从上到下匹配，匹配到第一个即停止（所以精准词在前，宽泛词在后）。

3. **多关键词支持**：每个分类支持多个关键词，用 `,` 分隔，输入中包含任一关键词即匹配。

4. **无匹配时**：如果 note 不包含任何关键词，模板会提示用户手动选择分类。

---

## 如何添加/修改规则

1. 在上表末尾添加新行
2. 序号使用下一个序号
3. 关键词用 `,` 分隔（不要加空格）
4. 如果需要调整优先级，可以移动整行到目标位置

---

## 分类参考（完整列表）

| 分类 | 英文 | Emoji |
|------|------|-------|
| 餐饮 | Food | 🍔 |
| 交通 | Transport | 🚌 |
| 购物 | Shopping | 🛍️ |
| 娱乐 | Entertainment | 🎮 |
| 医疗 | Health | 💊 |
| 教育 | Education | 📚 |
| 居住 | Housing | 🏠 |
| 通讯 | Communication | 📱 |
| 礼物 | Gift | 🎁 |
| 旅游 | Travel | ✈️ |
| 投资 | Investment | 💹 |
| 其他 | Other | ❓ |

---

> 关联：[[Expense Categories]] · [[Income Category Rules]] · [[Finance Dashboard]]