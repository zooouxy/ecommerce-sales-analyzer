# Ecommerce KPI Definitions / 电商 KPI 定义

## Metadata / 元数据
```yaml
domain: ecommerce_kpi
use_for: [KPI definition, metric meaning, interpretation boundaries]
do_not_use_for: [current metric values, current rankings]
structured_source_for_facts: sales_kpi / monthly_sales / product_performance / customer_value / customer_segments
```

# English

## Purpose
This document defines the meaning of core ecommerce KPIs used by the project. It defines concepts, not current values.

## Revenue
Revenue represents the sales value included by the project's analytical business rules. Use structured tools for the current value.

## Orders
Orders represent the number of distinct orders included by the project's analytical rules. Do not infer customer count from order count.

## Quantity
Quantity represents the number of product units included in the analysis. Quantity and order count are different measures.

## Average Order Value
Average Order Value (AOV) represents average revenue per order.

Conceptually:
```text
AOV = revenue / orders
```

The Agent should use the structured value returned by tools rather than recomputing it unless the user explicitly requests a calculation.

## Revenue Growth
Revenue growth compares revenue between periods. The project uses signed change semantics:
- positive = growth
- negative = decline

Month-over-month interpretation must respect month-completeness rules.

## Revenue Share
Revenue share represents an entity's contribution as a percentage of a broader revenue total.

When comparing two already-computed percentages, the project uses percentage-point difference rather than treating the percentages as raw revenue.

## Average Revenue per Customer
Average revenue per customer represents total segment revenue divided across customers in that segment.

It is not the same as Average Order Value.

## Product Revenue Concentration
Product revenue concentration describes how much revenue is represented by a defined group of leading products.

It should not automatically be interpreted as profitability or business risk without additional evidence.

## Metric Evidence Rule
Definitions may come from this document. Current values must come from structured tools.

---

# 中文

## 用途
本文档定义项目中核心电商 KPI 的含义。它负责定义概念，不负责提供当前数值。

## Revenue
Revenue 表示按照项目当前分析业务规则纳入统计的销售金额。当前收入数值必须通过结构化工具获取。

## Orders
Orders 表示按照分析规则纳入的独立订单数量。不能根据订单数直接推断客户数量。

## Quantity
Quantity 表示分析中纳入的商品件数。销量与订单数是不同指标。

## Average Order Value
平均订单价值（AOV）表示每个订单对应的平均收入。

概念上：
```text
AOV = revenue / orders
```

除非用户明确要求计算，否则 Agent 应优先使用 Tool 已返回的结构化数值，而不是自行重新计算。

## Revenue Growth
收入增长率用于比较不同周期之间的收入变化。项目使用有符号变化语义：
- 正值表示增长
- 负值表示下降

月度环比解释必须遵守月份完整性规则。

## Revenue Share
Revenue Share 表示某个实体对更大收入总量的贡献比例。

比较两个已经计算好的收入占比时，项目使用“百分点差”，而不是把两个百分比继续当作原始收入计算相对增长。

## Average Revenue per Customer
平均每客户收入表示某个客户分群总收入在该分群客户之间的平均贡献。

它与 Average Order Value 不是同一个指标。

## Product Revenue Concentration
商品收入集中度表示一个指定头部商品集合贡献了多少收入。

没有额外证据时，不能自动把集中度解释成利润水平或经营风险。

## 指标证据规则
指标定义可以来自本文档。当前业务数值必须来自结构化工具。
