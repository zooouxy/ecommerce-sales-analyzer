# Product Performance Playbook / 商品表现解读手册

## Metadata / 元数据
```yaml
domain: product_performance
use_for: [product metric interpretation, multi-metric product comparison, product recommendations]
do_not_use_for: [exact product revenue, exact quantity, exact order count, exact ranking]
structured_source_for_facts: product_performance / product_comparison / product_concentration
```

# English

## Purpose
This document explains how to interpret product revenue, quantity, and order count. Exact product metrics must come from structured analytical tools.

## Revenue
High product revenue indicates strong monetary contribution.

It does not automatically mean:
- highest unit demand
- highest purchase frequency
- highest profitability

Revenue should be interpreted as contribution to observed sales value.

## Quantity
High quantity indicates a large number of units sold.

High quantity can coexist with lower revenue when unit price is lower or products are commonly purchased in larger unit counts.

Do not treat quantity as equivalent to revenue.

## Orders
High order count indicates that a product appears across many distinct orders.

A product can have:
- high order count but moderate quantity per order
- high quantity but fewer orders
- high revenue but lower order frequency

Each metric represents a different business dimension.

## Pairwise Comparison
When comparing two products, the revenue winner, quantity winner, and order-count winner may differ.

If metrics disagree, report each winner separately.

Do not invent a unique overall winner unless the user supplies an explicit evaluation rule or weighting scheme.

## Product Identity
```text
StockCode = unique product key
Description = display field
```

Do not use Description as the unique analytical identifier.

## Recommendations
Recommendations should follow the observed metric pattern.

Examples:
- high revenue + high orders: protect availability and monitor sustained demand
- high quantity + lower revenue: review price positioning and unit economics if those data are available
- high revenue + lower orders: investigate whether value is driven by higher value per purchase

Do not claim margin, profitability, or stock risk unless those data are available.

---

# 中文

## 用途
本文档用于解释商品收入、销量和订单数的业务含义。商品精确指标必须来自结构化分析工具。

## Revenue
商品收入高表示该商品对观测销售额贡献较强。

但不自动意味着：
- 单位需求最高
- 购买频率最高
- 利润最高

收入应被解释为对销售金额的贡献。

## Quantity
销量高表示售出的商品件数多。

销量高但收入较低可能发生在单价较低，或单次订单购买件数较多的情况下。

不能把销量和收入视为同一个指标。

## Orders
订单数高表示该商品出现在更多独立订单中。

一个商品可能表现为：
- 订单数高，但每单件数一般
- 销量高，但订单数较少
- 收入高，但购买频次相对低

每个指标代表不同业务维度。

## 两两比较
比较两个商品时，收入胜者、销量胜者、订单数胜者可能不是同一个商品。

指标不一致时，应分别报告。

除非用户提供明确评价规则或权重，否则不要自行定义唯一整体赢家。

## 商品身份规则
```text
StockCode = 商品唯一键
Description = 展示字段
```

不能把 Description 当作唯一分析标识。

## 建议
建议应基于已观测指标组合。

例如：
- 高收入 + 高订单：优先保证供应和持续监测需求
- 高销量 + 相对低收入：如果存在价格或成本数据，可进一步检查价格定位与单位经济性
- 高收入 + 相对低订单：可进一步分析是否由更高单次购买价值驱动

如果没有利润、毛利或库存数据，不应声称利润水平或缺货风险。
