/*
Query: Data Coverage
Purpose:
返回订单数据的起始时间和结束时间，用于判断边界月份是否为完整月份。
*/

SELECT
    MIN(invoice_date) AS data_start_date,
    MAX(invoice_date) AS data_end_date
FROM orders;