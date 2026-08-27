/*
====================================================
Customer RFM Scores

Purpose:
Convert customer RFM metrics into business scores.

This file calculates:

R Score:
Customer purchase recency score.

F Score:
Customer purchase frequency score.

M Score:
Customer monetary value score.

Generate:
rfm_code
rfm_score

Business Question:
"How valuable is each customer?"

This file controls:
- RFM scoring thresholds

Business Rule Source:
docs/Business_Rules.md
src/business_rules.py

Validation:
src/check_rfm_consistency.py

Status:
PASS

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
),
rfm_scores AS (
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary,

        CASE
            WHEN recency_days <= 12 THEN 5
            WHEN recency_days <= 32 THEN 4
            WHEN recency_days <= 71 THEN 3
            WHEN recency_days <= 178 THEN 2
            ELSE 1
        END AS r_score,

        CASE
            WHEN frequency >= 8 THEN 5
            WHEN frequency >= 4 THEN 4
            WHEN frequency >= 3 THEN 3
            WHEN frequency >= 2 THEN 2
            ELSE 1
        END AS f_score,

        CASE
            WHEN monetary >= 5000 THEN 5
            WHEN monetary >= 2000 THEN 4
            WHEN monetary >= 800 THEN 3
            WHEN monetary >= 300 THEN 2
            ELSE 1
        END AS m_score

    FROM rfm_base
)

SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    r_score || f_score || m_score AS rfm_code,
    r_score + f_score + m_score AS rfm_score
FROM rfm_scores;
*/

/*
====================================================
Customer RFM Scores View

Purpose:
Convert raw RFM metrics into business scores.

Input:
customer_rfm_base

Output:
r_score
f_score
m_score
rfm_score

Business Rule Source:
src/business_rules.py

====================================================
*/
/*
View Name:
customer_rfm_scores

Purpose:
根据business_rules.py中的RFM评分规则，
将客户划分为R/F/M五档评分。

Input:
customer_rfm_base

Output:
customer_id
r_score
f_score
m_score
rfm_score
*/

CREATE VIEW IF NOT EXISTS customer_rfm_scores AS

WITH scored AS (

SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,

    CASE
        WHEN recency_days <= 12 THEN 5
        WHEN recency_days <= 32 THEN 4
        WHEN recency_days <= 71 THEN 3
        WHEN recency_days <= 178 THEN 2
        ELSE 1
    END AS r_score,

    CASE
        WHEN frequency >= 8 THEN 5
        WHEN frequency >= 4 THEN 4
        WHEN frequency >= 3 THEN 3
        WHEN frequency >= 2 THEN 2
        ELSE 1
    END AS f_score,

    CASE
        WHEN monetary >= 5000 THEN 5
        WHEN monetary >= 2000 THEN 4
        WHEN monetary >= 800 THEN 3
        WHEN monetary >= 300 THEN 2
        ELSE 1
    END AS m_score

FROM customer_rfm_base

)

SELECT
    *,
    r_score || f_score || m_score AS rfm_code,
    r_score + f_score + m_score AS rfm_score

FROM scored;