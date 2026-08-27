/*
====================================================
Customer Segmentation

Purpose:
Classify customers into business segments
based on RFM scores.

Segments:

Champions:
High activity, high frequency,
high monetary customers.

Loyal Customers:
Active customers with strong purchasing behavior.

Big Spenders:
High spending customers with lower frequency.

High Value Lost:
Previously valuable customers who became inactive.

At Risk:
Customers showing possible churn risk.

Lost Customers:
Low activity and low value customers.

Regular Customers:
Remaining customers.

Business Question:
"Which customers need which business actions?"

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
),
customer_segments AS (
    SELECT
        *,
        r_score + f_score + m_score AS rfm_score,

        CASE
            WHEN r_score = 5
             AND f_score = 5
             AND m_score = 5
            THEN 'Champions'

            WHEN r_score >= 4
             AND f_score >= 4
            THEN 'Loyal Customers'

            WHEN r_score >= 4
             AND m_score = 5
             AND f_score <= 3
            THEN 'Big Spenders'

            WHEN r_score <= 2
             AND m_score >= 4
            THEN 'High Value Lost'

            WHEN r_score <= 2
             AND f_score >= 3
            THEN 'At Risk'

            WHEN r_score <= 2
             AND f_score <= 2
             AND m_score <= 2
            THEN 'Lost Customers'

            ELSE 'Regular Customers'

        END AS segment

    FROM rfm_scores
)

SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(monetary),2) AS total_revenue,
    ROUND(AVG(monetary),2) AS avg_customer_revenue,
    ROUND(
        SUM(monetary) * 100.0 /
        SUM(SUM(monetary)) OVER(),
        2
    ) AS revenue_percentage
FROM customer_segments
GROUP BY segment
ORDER BY total_revenue DESC;
*/

/*
====================================================
Customer Segmentation View

Purpose:
Assign customers into business segments.

Input:
customer_rfm_scores

Output:
customer segment

Business Rule:
docs/Business_Rules.md

====================================================
*/
/*
View Name:
customer_segments

Purpose:
根据RFM评分结果进行客户分层。

Segments:
Champions
Loyal Customers
Big Spenders
High Value Lost
At Risk
Lost Customers
Regular Customers

Used For:
Customer analytics
Agent business queries
*/

CREATE VIEW IF NOT EXISTS customer_segments AS

SELECT
    *,
    CASE

        WHEN r_score = 5
         AND f_score = 5
         AND m_score = 5
        THEN 'Champions'

        WHEN r_score >= 4
         AND f_score >= 4
        THEN 'Loyal Customers'

        WHEN r_score >= 4
         AND m_score = 5
         AND f_score <= 3
        THEN 'Big Spenders'

        WHEN r_score <= 2
         AND m_score >= 4
        THEN 'High Value Lost'

        WHEN r_score <= 2
         AND f_score >= 3
        THEN 'At Risk'

        WHEN r_score <= 2
         AND f_score <= 2
         AND m_score <= 2
        THEN 'Lost Customers'

        ELSE 'Regular Customers'

    END AS segment

FROM customer_rfm_scores;