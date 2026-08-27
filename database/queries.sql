/*
Deprecated SQL Query Collection

This file is no longer used as the active business query source.

Queries have been migrated to:

database/sql/
    01_sales_kpis.sql
    02_monthly_sales.sql
    03_customer_value.sql
    04_product_performance.sql
    05_product_concentration.sql
    09_business_queries.sql

RFM logic has been migrated to database views:

database/views/
    06_customer_rfm_base.sql
    07_customer_rfm_scores.sql
    08_customer_segments.sql

Important:
- Do not define RFM scoring with NTILE here.
- Do not recompute customer segments here.
- Use customer_segments View for segment-based business queries.
*/