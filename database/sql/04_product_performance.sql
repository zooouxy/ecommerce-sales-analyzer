/*
Query: Product Performance
Purpose:
分析有效商品的收入、销量和订单表现，并提供商品综合表现排名。

Business Questions:
- 哪些商品贡献最高收入？
- 哪些商品销量最高？
- 哪些商品具有较高综合表现？

Business Rules:
排除邮费、人工调整、平台费用、坏账、样品等非标准商品记录。
*/

WITH valid_products AS (
    SELECT
        p.stock_code,
        p.description
    FROM products p
    WHERE p.stock_code NOT IN (
    'DOT',
    'M',
    'POST',
    'AMAZONFEE',
    'B',
    'C2',
    '23444',
    'BANK CHARGES',
    '23574',
    'S'
    )
),
product_metrics AS (
    SELECT
        oi.stock_code,
        vp.description,
        ROUND(SUM(oi.sales), 2) AS revenue,
        SUM(oi.quantity) AS quantity,
        COUNT(DISTINCT oi.order_id) AS orders
    FROM order_items oi
    JOIN valid_products vp ON oi.stock_code = vp.stock_code
    GROUP BY oi.stock_code, vp.description
)
SELECT
    stock_code,
    description,
    revenue,
    quantity,
    orders
FROM product_metrics
ORDER BY revenue DESC;