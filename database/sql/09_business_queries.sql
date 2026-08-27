/*
Query: Customer Segment Business Summary
Purpose:
基于已冻结的 customer_segments View，
汇总各客户分群的人数、收入、收入贡献和平均客户收入。

Business Questions:
- 每个客户分群有多少客户？
- 每个分群贡献多少收入？
- 每个分群收入占比是多少？
- 每个分群的平均客户价值是多少？

Business Rules:
RFM评分与客户分群逻辑由 database/views 下的RFM Views统一负责。
本查询不重复计算RFM或Segment规则。
*/

SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(monetary), 2) AS total_revenue,
    ROUND(
        SUM(monetary) * 100.0
        / (SELECT SUM(monetary) FROM customer_segments),
        2
    ) AS revenue_percentage,
    ROUND(AVG(monetary), 2) AS average_revenue_per_customer
FROM customer_segments
GROUP BY segment
ORDER BY total_revenue DESC;