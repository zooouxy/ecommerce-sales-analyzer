/*
View/Query: Sales KPIs
Purpose:
提供整体销售核心指标，包括收入、订单量、商品数量和平均订单金额。

Business Questions:
- 总收入是多少？
- 总订单数是多少？
- 总销售数量是多少？
- 平均每笔订单金额是多少？
*/

SELECT
    ROUND(SUM(oi.sales), 2) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS total_quantity,
    ROUND(SUM(oi.sales) / COUNT(DISTINCT o.order_id), 2) AS average_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id;