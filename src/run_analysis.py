import pandas as pd

from src.sales_analysis import (
    calculate_sales_kpis,
    monthly_sales_trend,
    top_products_by_revenue,
    sales_by_country
)

from src.customer_analysis import (
    customer_revenue,
    customer_order_frequency,
    customer_average_order_value
)

from src.product_analysis import (
    product_revenue,
    product_quantity,
    product_order_count
)

from src.rfm_analysis import (
    build_rfm_table,
    calculate_rfm_scores,
    show_rfm_score_ranges,
    assign_customer_segment,
    summarize_customer_segments,
    generate_business_insights
)


df = pd.read_csv(
    "data/processed/cleaned_sales.csv",
    dtype={
        "InvoiceNo": str,
        "StockCode": str
    }
)

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"]
)

kpis = calculate_sales_kpis(df)

# Sales Analysis
print("Sales KPIs")
print("----------------")

for key, value in kpis.items():
    print(
        f"{key}: {value}"
    )

# Top products by revenue
print("\nTop Products")
print("----------------")

top_products = top_products_by_revenue(df)

print(top_products)

# Sales by country
print("\nTop Countries")
print("----------------")

country_sales = sales_by_country(df)

print(
    country_sales.head(10)
)

# Monthly sales trend
print("\nMonthly Sales Trend")
print("----------------")

monthly_sales = monthly_sales_trend(df)

print(monthly_sales)

# Customer analysis
print("\nTop Customers by Revenue")
print("----------------")

print(
    customer_revenue(df).head(10)
)


print("\nTop Customers by Order Frequency")
print("----------------")

print(
    customer_order_frequency(df).head(10)
)


print("\nTop Customers by Average Order Value")
print("----------------")

print(
    customer_average_order_value(df).head(10)
)

# Product analysis
print("\nTop Products by Revenue")
print("----------------")

print(
    product_revenue(df).head(10)
)


print("\nTop Products by Quantity")
print("----------------")

print(
    product_quantity(df).head(10)
)


print("\nTop Products by Order Count")
print("----------------")

print(
    product_order_count(df).head(10)
)

print("\nRFM Analysis")
print("----------------")

# 构建 RFM 基础表
rfm = build_rfm_table(df)
print("\nRFM Customers")
print("----------------")
print(
    rfm.head(10)
)
# 计算 RFM 五分制评分
rfm = calculate_rfm_scores(rfm)

# 按 RFM 总分从高到低排列
# 用于找出综合价值最高的客户
# top_rfm_customers = rfm.sort_values(
#     "RFM_Score",
#     ascending=False
# )
#
# print("\nTop RFM Customers")
# print("----------------")
#
# # 查看综合 RFM 得分最高的前 10 位客户
# print(
#     top_rfm_customers.head(10)
# )
#
# # 查看 R、F、M 五分位数的实际数据边界
# show_rfm_score_ranges(rfm)

# 根据 RFM 指标对客户进行分层
rfm = assign_customer_segment(rfm)
print("\nCustomer Segments")
print("----------------")

# 统计每个客户群体的人数
segment_counts = (
    rfm["Segment"]
    .value_counts()
)

print(segment_counts)

# 汇总不同客户群体的业务表现
segment_summary = summarize_customer_segments(rfm)

print("\nSegment Business Summary")
print("----------------")
# 使用 to_string() 完整显示 DataFrame，避免终端自动折叠列
print(segment_summary.to_string())

# 根据客户分层结果生成正式的 Business Insights
business_insights = generate_business_insights(
    segment_summary
)

print("\nBusiness Insights Summary")
print("----------------")

# 逐条输出 Business Insight
for insight_name, insight_text in business_insights.items():
    print(f"\n{insight_name}")
    print(insight_text)