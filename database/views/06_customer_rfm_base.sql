/*
====================================================
Customer RFM Base Metrics

Purpose:
Generate customer-level RFM raw metrics.

This file calculates:

1. Recency:
   Days since customer's latest purchase.

2. Frequency:
   Number of distinct orders.

3. Monetary:
   Total customer revenue.

Business Question:
"What is each customer's historical purchasing behavior?"

Output:
customer_id
recency_days
frequency
monetary

This file does NOT include:
- RFM scoring
- Customer segmentation

Business Rule Reference:
docs/Business_Rules.md
src/business_rules.py

====================================================
*/
/*
WITH customer_rfm AS (
    SELECT
        o.customer_id,
        MAX(o.invoice_date) AS last_purchase_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(oi.sales),2) AS monetary
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
),
rfm_base AS (
    SELECT
        customer_id,
        CAST(
            julianday((SELECT MAX(invoice_date) FROM orders))
            - julianday(last_purchase_date)
            AS INTEGER
        ) AS recency_days,
        frequency,
        monetary
    FROM customer_rfm
)

SELECT
    customer_id,
    recency_days,
    frequency,
    monetary
FROM rfm_base;
*/

/*
====================================================
Customer RFM Base View

Purpose:
Create customer-level RFM raw metrics.

Output:
customer_id
recency_days
frequency
monetary

This view provides the foundation
for RFM scoring.

Business Rule Reference:
docs/Business_Rules.md

====================================================
*/
/*
View Name:
customer_rfm_base

Purpose:
计算客户基础RFM指标。

Business Definition:
R:
距离最后一次购买的天数

F:
客户历史订单数量

M:
客户累计消费金额

Used By:
07_customer_rfm_scores.sql
*/

CREATE VIEW customer_rfm_base AS

WITH customer_rfm AS (

    SELECT
        o.customer_id,
        MAX(o.invoice_date) AS last_purchase_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(oi.sales),2) AS monetary
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id

)

SELECT
    customer_id,

    CAST(
        julianday(
            (SELECT MAX(invoice_date) FROM orders)
        )
        -
        julianday(last_purchase_date)
        AS INTEGER
    ) AS recency_days,

    frequency,
    monetary

FROM customer_rfm;