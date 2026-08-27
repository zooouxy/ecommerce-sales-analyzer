/*
Query: Monthly Sales
Purpose:
按月汇总销售收入和订单数量，并计算销售收入环比增长率。

Business Questions:
- 每个月的销售收入是多少？
- 每个月有多少订单？
- 月度收入环比增长率是多少？
*/

WITH monthly_sales AS (
    SELECT
        strftime('%Y-%m', o.invoice_date) AS month,
        ROUND(SUM(oi.sales), 2) AS revenue,
        COUNT(DISTINCT o.order_id) AS orders
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY strftime('%Y-%m', o.invoice_date)
),
monthly_growth AS (
    SELECT
        month,
        revenue,
        orders,
        LAG(revenue) OVER (ORDER BY month) AS previous_revenue
    FROM monthly_sales
)
SELECT
    month,
    revenue,
    orders,
    ROUND(
        CASE
            WHEN previous_revenue IS NULL OR previous_revenue = 0 THEN NULL
            ELSE (revenue - previous_revenue) * 100.0 / previous_revenue
        END,
        2
    ) AS revenue_growth_pct
FROM monthly_growth
ORDER BY month;