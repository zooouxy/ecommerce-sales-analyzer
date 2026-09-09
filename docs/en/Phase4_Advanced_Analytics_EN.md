# Phase 4 — Advanced Analytics & Business Reasoning

## 1. Phase Goal

Phase 4 upgrades the project from deterministic data lookup to deterministic business reasoning while preserving the frozen access path:

```text
User
→ LLM / Agent
→ Tool
→ Query Service
→ SQL / View
→ SQLite
```

The LLM does not query the database directly and does not own core business calculations. Trend detection, pairwise comparisons, differences, percentage differences, completeness rules, and metric winners are computed deterministically in Python / SQL and exposed through tools.

Phase 4 intentionally focuses on two portfolio-relevant capabilities:

1. Trend Insight
2. Comparison Analytics

It does not expand into forecasting, anomaly detection, seasonality modeling, causal attribution, or a generic planning framework.

## 2. Trend Insight

### 2.1 Monthly Trend Insight

The monthly trend service returns:

- highest revenue month
- highest order month
- largest revenue growth month
- largest revenue decline month
- latest month
- data coverage boundaries
- partial-month status

### 2.2 Complete-Month Business Rule

Monthly rankings use complete months only.

Month-over-month comparisons require both the current month and the previous month to be complete.

The latest dataset month is still returned when incomplete, but it is explicitly marked:

```text
is_partial_month = True
```

This prevents a partial month from being interpreted as a normal full-period decline.

### 2.3 Verified Trend Results

```text
Highest revenue month:
2011-11
Revenue: 1,509,496.33
Orders: 2,769
Revenue growth: 30.69%

Highest order month:
2011-11

Largest revenue growth:
2011-05
Revenue: 770,536.02
Orders: 1,681
Revenue growth: 43.27%

Largest revenue decline:
2011-04
Revenue: 537,808.62
Orders: 1,246
Revenue growth: -25.06%

Latest month:
2011-12
Revenue: 638,792.68
Orders: 819
Revenue growth: -57.68%
is_partial_month: True
```

Dataset coverage:

```text
Start: 2010-12-01 08:26:00
End:   2011-12-09 12:50:00
```

## 3. Comparison Analytics

Phase 4 adds deterministic pairwise comparison services instead of asking the LLM to manually compare raw records.

The common comparison direction is:

```text
difference = B - A
```

For ordinary numeric metrics:

```text
percentage_difference = (B - A) / A × 100
```

The comparison layer also exposes semantic fields such as:

```text
direction
magnitude
magnitude_pct
higher_xxx
```

These fields allow the Agent to explain comparisons without recomputing numbers.

## 4. Month Comparison

`month_comparison` compares two explicitly specified months.

Compared metrics:

- revenue
- orders

Returned fields include:

- signed difference
- percentage difference
- direction
- absolute magnitude
- higher-revenue month
- higher-order month
- partial-month list
- full-comparability flag

Verified example:

```text
2011-10 vs 2011-11

Revenue difference: +354,517.03
Revenue difference pct: +30.69%

Orders difference: +729
Orders difference pct: +35.74%

comparison_is_fully_comparable = True
```

Partial-month example:

```text
2011-11 vs 2011-12

comparison_is_fully_comparable = False
partial_months = ["2011-12"]
```

The tool still returns observed values, but the Agent must not treat the comparison as a fair full-month comparison.

## 5. Product Comparison

`product_comparison` compares two explicitly specified StockCodes.

Product identity remains:

```text
StockCode = unique key
Description = display field only
```

Compared metrics:

- revenue
- quantity
- orders

Verified example:

```text
22423 vs 85123A

Higher revenue product:
22423

Higher quantity product:
85123A

Higher order product:
85123A
```

Verified differences:

```text
Revenue difference:
-68,013.46
-38.98%

Quantity difference:
+24,073
+173.45%

Orders difference:
+277
+13.93%
```

Different metrics can have different winners. If the user does not define a combined evaluation rule, the Agent reports metric-level winners rather than inventing one overall winner.

Missing StockCodes are returned through:

```text
missing_stock_codes
```

instead of being treated as system failures.

## 6. Customer Segment Comparison

`segment_comparison` compares two customer segments using the existing RFM business summary.

Compared metrics:

- customer_count
- total_revenue
- revenue_percentage
- average_revenue_per_customer

For `revenue_percentage`, the difference is expressed in percentage points:

```text
revenue_percentage_difference_pp
```

rather than as another relative percentage-growth calculation.

Verified example:

```text
Champions vs Loyal Customers

Customer count:
Loyal Customers higher

Total revenue:
Champions higher

Revenue percentage:
Champions higher

Average revenue per customer:
Champions higher
```

Verified values:

```text
Customer count difference:
+739
+499.32%

Total revenue difference:
-626,951.58
-19.48%

Revenue percentage difference:
-7.03 percentage points

Average revenue per customer difference:
-18,822.80
-86.57%
```

Mixed metric winners do not automatically imply one overall winner.

## 7. Tool Layer

Phase 4 adds:

```text
monthly_trend_insights
month_comparison
product_comparison
segment_comparison
```

Current core tool set:

```text
sales_kpi
monthly_sales
monthly_trend_insights
month_comparison
customer_value
product_performance
product_comparison
product_concentration
customer_segments
segment_comparison
```

Routing remains:

```text
Agent
→ Tool Router
→ Tool
→ Query Service
→ SQL / SQLite
```

## 8. Grounding and Reliability Improvements

Phase 4 keeps grounding lightweight and deterministic.

Current deterministic checks include:

- tool execution success
- unsupported numeric claims
- unsupported currency / monetary units
- evidence from tool-call arguments
- evidence from tool results

Comparison services expose structured semantic fields so the LLM does not need to recompute:

- signed differences
- absolute magnitudes
- percentage differences
- comparison direction
- higher-value entities

The Agent also includes programmatic duplicate-call suppression:

```text
same tool + same arguments + previous successful result
→ reuse existing result
→ do not execute the tool again
```

For more stable factual generation, the SiliconFlow provider uses:

```text
temperature = 0
```

This reduces variability but does not replace grounding validation.

## 9. Regression and Acceptance Testing

### 9.1 Tool Regression

Verified tools:

```text
sales_kpi                 PASS
monthly_sales             PASS
monthly_trend_insights    PASS
month_comparison          PASS
customer_value            PASS
product_performance       PASS
product_comparison        PASS
product_concentration     PASS
customer_segments         PASS
segment_comparison        PASS
```

Result:

```text
ALL PHASE 4 TOOL REGRESSION TESTS PASSED
```

### 9.2 Agent Regression

Validated end-to-end paths:

```text
Overall sales overview
→ sales_kpi

Highest revenue month
→ monthly_trend_insights

Month-to-month comparison
→ month_comparison

Product-to-product comparison
→ product_comparison

Segment-to-segment comparison
→ segment_comparison
```

All tested answers passed grounding validation.

### 9.3 Streamlit Validation

The Streamlit AI Analyst was validated for:

- overall KPI analysis
- trend insight
- month comparison
- product comparison
- segment comparison
- Agent Trace rendering
- grounding result rendering

The tested Phase 4 scenarios completed successfully through the UI.

## 10. Known Limitations

Phase 4 intentionally does not attempt full semantic answer verification.

Current limitations include:

- Grounding validation verifies direct numeric and metadata evidence but does not fully detect semantic contradictions.
- A response may contain correct numbers but still describe a higher/lower relationship incorrectly.
- Full comparison-direction and contradiction checking is deferred to a later semantic validation layer.
- Relative-time expressions remain limited and may require clarification.
- Currency metadata is not currently exposed by analytical tools.
- Monetary values should therefore be displayed without inventing a currency.
- LLM generation remains probabilistic even with low temperature.
- Very large compound requests may exceed the configured maximum number of tool rounds.
- Streamlit chat history remains UI-level history rather than full cross-question Agent memory.

These limitations are documented to clearly separate deterministic guarantees from LLM interpretation.

## 11. Phase 4 Status

```text
Phase 4 — Advanced Analytics & Business Reasoning
✅ COMPLETE

Trend Insight
✅ COMPLETE

Month Comparison
✅ COMPLETE

Product Comparison
✅ COMPLETE

Customer Segment Comparison
✅ COMPLETE

Tool Regression
✅ PASS

Agent Regression
✅ PASS

Streamlit Validation
✅ PASS
```

Phase 4 is ready to be frozen before moving to the next project stage.
