from src.tools import (
    sales_kpi_tool,
    monthly_sales_tool,
    customer_value_tool,
    product_performance_tool,
    product_concentration_tool,
    customer_segments_tool
)


assert sales_kpi_tool()["total_orders"] == 19960

assert monthly_sales_tool("2011-11")[0]["revenue"] == 1509496.33

assert customer_value_tool(customer_id=14646)[0]["customer_id"] == 14646

assert product_performance_tool(stock_code="22423")[0]["stock_code"] == "22423"

assert product_concentration_tool()["top_10_revenue_share_pct"] == 9.45

assert customer_segments_tool("Champions")[0]["customer_count"] == 148

print("Agent Tool Layer Test: PASS")