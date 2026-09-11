# Sales Trend Interpretation / 销售趋势解读规范

## Metadata / 元数据
```yaml
domain: sales_trend
use_for: [trend interpretation, partial-month interpretation, growth/decline explanation]
do_not_use_for: [exact monthly revenue, exact monthly orders, exact growth percentage]
structured_source_for_facts: monthly_sales / monthly_trend_insights / month_comparison
```

# English

## Purpose
This document defines how monthly sales trends should be interpreted after deterministic metrics have already been calculated. Exact revenue, order volume, growth rates, rankings, and month completeness must come from structured analytical tools.

## Growth
A positive month-over-month revenue change means observed revenue in the current period is higher than in the comparison period.

A positive result alone does not establish the cause. Do not automatically attribute growth to marketing, seasonality, pricing, product launches, or acquisition without supporting evidence.

## Decline
A negative month-over-month revenue change means observed revenue is lower than in the comparison period.

Before describing this as business deterioration, check:
- month completeness
- order movement
- product mix
- customer mix
- other available evidence

## Partial Month
A partial month is not directly comparable with a complete month as if both represented equal calendar coverage.

When a month is marked partial:
- report observed values
- explicitly mention incomplete coverage
- avoid declaring a normal full-month winner or loser
- avoid interpreting the apparent decline as a complete-period trend

## Complete-Month Ranking
Monthly trend ranking should use complete months only, including:
- highest revenue month
- highest order month
- strongest growth month
- largest decline month

## Multi-Metric Interpretation
Revenue and order volume can move differently. When indicators disagree, describe them separately instead of forcing one overall conclusion.

## Evidence Rule
```text
Structured metric
→ completeness check
→ business interpretation
```

RAG explains what a result may mean. It must not invent the numeric result or an unsupported cause.

---

# 中文

## 用途
本文档规定在确定性指标已经计算完成之后，如何解释月度销售趋势。收入、订单量、增长率、排名以及月份完整性等精确事实必须来自结构化分析工具。

## 增长
正向月度收入变化表示当前比较周期的观测收入高于基准周期。

但“增长”本身不能证明增长原因。除非有额外证据，不应自动归因于营销、季节性、定价、新品发布或拉新。

## 下降
负向月度收入变化表示当前比较周期的观测收入低于基准周期。

在得出“业务恶化”等结论前，应检查：
- 月份完整性
- 订单变化
- 商品结构
- 客户结构
- 其他可用证据

## Partial Month
部分月份不能像两个覆盖范围相同的完整月份一样直接比较。

当月份被标记为 partial 时：
- 可以报告当前已观测数值
- 必须明确说明数据覆盖不完整
- 不应直接定义正常的完整月赢家或输家
- 不应把表面下降直接解释为完整周期趋势

## 完整月份排名
月度趋势排名只应使用完整月份，包括：
- 收入最高月份
- 订单数最高月份
- 增长最快月份
- 下降最大月份

## 多指标解读
收入和订单数可能出现不同方向。指标不一致时，应分别说明，不要强行归纳成唯一整体结论。

## 证据规则
```text
结构化指标
→ 完整性检查
→ 业务解释
```

RAG 层只负责解释结果可能意味着什么，不负责编造数值或未经证实的原因。
