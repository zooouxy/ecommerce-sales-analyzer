/*
Query: Customer Value
Purpose:
按客户汇总历史订单行为和累计消费金额，用于识别高价值客户。

Business Questions:
- 哪些客户贡献了最多收入？
- 每个客户有多少订单？
- 每个客户累计消费金额是多少？
- 每个客户平均订单金额是多少？
*/

SELECT
    o.customer_id,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.sales), 2) AS total_revenue,
    ROUND(SUM(oi.sales) / COUNT(DISTINCT o.order_id), 2) AS average_order_value,
    MIN(o.invoice_date) AS first_purchase_date,
    MAX(o.invoice_date) AS last_purchase_date
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.customer_id IS NOT NULL
GROUP BY o.customer_id
ORDER BY total_revenue DESC;