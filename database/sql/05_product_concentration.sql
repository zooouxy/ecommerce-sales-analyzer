/*
Query: Product Concentration
Purpose:
计算有效商品收入集中度，衡量头部商品对总收入的贡献。

Business Questions:
- Top 10商品贡献多少收入？
- Top 10商品占全部有效商品收入的比例是多少？

Business Rules:
排除邮费、人工调整、平台费用、坏账、样品等非标准商品记录。
商品过滤规则应与04_product_performance.sql保持一致。
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
product_revenue AS (
    SELECT
        oi.stock_code,
        vp.description,
        ROUND(SUM(oi.sales), 2) AS revenue
    FROM order_items oi
    JOIN valid_products vp ON oi.stock_code = vp.stock_code
    GROUP BY oi.stock_code, vp.description
),
ranked_products AS (
    SELECT
        stock_code,
        description,
        revenue,
        ROW_NUMBER() OVER (ORDER BY revenue DESC) AS revenue_rank
    FROM product_revenue
),
revenue_summary AS (
    SELECT
        ROUND(SUM(revenue), 2) AS total_product_revenue,
        ROUND(SUM(CASE WHEN revenue_rank <= 10 THEN revenue ELSE 0 END), 2) AS top_10_revenue
    FROM ranked_products
)
SELECT
    total_product_revenue,
    top_10_revenue,
    ROUND(top_10_revenue * 100.0 / total_product_revenue, 2) AS top_10_revenue_share_pct
FROM revenue_summary;