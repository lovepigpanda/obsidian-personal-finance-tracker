---
title: Finance Category Quick Reference — AI Agent 快速参考
created: 2026-06-01
updated: 2026-06-01
version: V1.0
status: ACTIVE
type: quick-reference
tags: [agent, finance, reference]
description: AI Agent 快速查找的分类和账户参考（结构化格式）
---

# AI Agent 快速参考（结构化）

> 本文件供 AI Agent 程序化读取，提供分类映射、账户映射、文件格式规范。

---

## 支出分类（Expense Categories）

| 分类 | 英文名 | Emoji | 关键词 |
|------|--------|-------|--------|
| Food | Food | 🍔 | 午餐,晚餐,早餐,外卖,餐厅,吃饭,餐饮,沙县,兰州,快餐,食堂,早点,夜宵,烧烤,火锅 |
| Transport | Transport | 🚌 | 地铁,公交,打车,taxi,uber,停车,加油,高铁,火车,出行,滴滴,顺风车,骑行 |
| Shopping | Shopping | 🛍️ | 淘宝,京东,拼多多,购物,衣服,鞋子,超市,日用品,百货,电器,数码,手机 |
| Entertainment | Entertainment | 🎮 | 电影,游戏,音乐,视频,爱奇艺,腾讯视频,steam,奈飞,会员,订阅,唱K,ktv |
| Health | Health | 💊 | 医院,药店,买药,体检,牙科,中医,门诊,医疗,看病,挂号 |
| Education | Education | 📚 | 课程,学费,书籍,培训,考试,订阅,edu,学习,教程,课外班 |
| Housing | Housing | 🏠 | 房租,物业,水电,燃气,维修,家居,装修,家政,保洁 |
| Communication | Communication | 📱 | 手机,话费,宽带,流量,通讯,固话 |
| Gift | Gift | 🎁 | 红包,礼物,请客,人情,送礼物,份子钱 |
| Travel | Travel | ✈️ | 机票,酒店,旅游,门票,旅行,度假,景区 |
| Investment | Investment | 💹 | 理财,基金,股票,投资,亏损 |
| Other | Other | ❓ | 其他,杂项 |

## 收入分类（Income Categories）

| 分类 | 英文名 | Emoji | 关键词 |
|------|--------|-------|--------|
| Salary | Salary | 💰 | 工资,月薪,薪资,底薪,发工资,工资到账,工资发放 |
| Bonus | Bonus | 🎉 | 年终奖,奖金,绩效,分红,年奖,季度奖,项目奖金 |
| Freelance | Freelance | 💻 | 兼职,外快,接单,私活,自由职业,freelance,接活 |
| Investment | Investment | 📈 | 理财,利息,投资收益,基金分红,股票收益,股息,分红 |
| Refund | Refund | 🔄 | 退款,退货,补偿,赔偿,赔付 |
| Gift | Gift | 🎁 | 红包,礼金 |
| Other | Other | ❓ | 其他,偶然收入 |

## 账户映射（Account Mapping）

| 账户名 | 类型 | 关键词 |
|--------|------|--------|
| Alipay | e-wallet | 支付宝 |
| WeChat Pay | e-wallet | 微信,微信支付 |
| CMB | bank | 招行,招商银行 |
| ICBC | bank | 工行,工商银行 |
| Credit Card | credit-card | 信用卡,贷记卡 |
| Cash | cash | 现金 |
| USD Account | bank | 美元账户,USD |

## 支付方式（Payment Methods）

| 方式 | 关键词 |
|------|--------|
| Alipay | 支付宝 |
| WeChat Pay | 微信,微信支付 |
| Bank Transfer | 银行转账,招行,工行 |
| Credit Card | 信用卡 |
| Debit Card | 借记卡 |
| Cash | 现金 |

## 币种（Currency）

| 币种 | 代码 | 关键词 |
|------|------|--------|
| 人民币 | CNY | 元,块,块 |
| 美元 | USD | 刀,刀,美元,dollar |
| 欧元 | EUR | 欧元,euro |
| 日元 | JPY | 日元,円 |
| 港币 | HKD | 港币,HK |

## 文件命名规范（AI 生成文件名）

### 支出文件
```
Transactions/expenses/{YYYY-MM-DD}-{description}-{amount}-{CURRENCY}-{STATUS}.md
```
示例：`Transactions/expenses/2026-06-01-lunch-45-CNY-ACTIVE.md`

### 收入文件
```
Transactions/incomes/{YYYY-MM-DD}-{description}-{amount}-{CURRENCY}-{STATUS}.md
```
示例：`Transactions/incomes/2026-06-01-salary-15000-CNY-ACTIVE.md`

## Frontmatter 模板（AI 生成）

```yaml
---
type: expense                    # 或 income
date: YYYY-MM-DD
amount: 数字
currency: CNY                    # CNY/USD/EUR/JPY/HKD
category: CategoryName
account: AccountName
payment_method: PaymentMethod
note: "用户原始描述"
tags: [expense, categoryName]    # expense 或 income + 分类名
status: ACTIVE
created: YYYY-MM-DD
---
```

## 时间转换规则

| 用户输入 | 转换为 |
|---------|--------|
| 今天 | 当前日期（2026-06-01） |
| 昨天 | 当前日期 - 1天 |
| 前天 | 当前日期 - 2天 |
| 上周 | 本周一 |
| 上个月 | 上月1日 |

## 金额提取规则

| 用户输入 | 提取 |
|---------|------|
| "45元" | amount=45, currency=CNY |
| "15000" | amount=15000, currency=CNY（默认） |
| "35美元" | amount=35, currency=USD |
| "€50" | amount=50, currency=EUR |
| "15000元" | amount=15000, currency=CNY |

---

## AI Agent 标准工作流

```
1. 读取用户自然语言输入
2. 判断 type：支出 ("花了","买了","消费","付了") → expense
                   收入 ("收到","进账","赚了","工资") → income
3. 提取 date：时间词 → YYYY-MM-DD
4. 提取 amount + currency：数字 + 币种
5. 匹配 account：支付工具 → 账户名
6. 匹配 payment_method：同上
7. 匹配 category：根据 note 关键词查上方分类表
8. 生成 filename：{date}-{description}-{amount}-{currency}-ACTIVE.md
9. 写入 Transactions/expenses/ 或 Transactions/incomes/
10. 返回完成信息给用户
```

---

## 文件路径汇总

| 文件 | 路径 |
|------|------|
| 支出规则 | `Categories/expense-category-rules.md` |
| 收入规则 | `Categories/income-category-rules.md` |
| 支出模板 | `Templates/expense-template.md` |
| 收入模板 | `Templates/income-template.md` |
| 仪表盘 | `Dashboards/finance-dashboard.md` |
| 账户列表 | `Accounts/account-list.md` |
| 本文件 | `QUICK-REFERENCE.md` |

---

> AI Agent 使用 | 创建于：2026-06-01