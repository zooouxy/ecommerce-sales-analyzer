from src.tool_router import run_tool


# ===============================
# Successful Tool Calls
# ===============================

sales_result = run_tool(
    "sales_kpi"
)

assert sales_result["success"] is True
assert sales_result["tool"] == "sales_kpi"
assert sales_result["data"]["total_orders"] == 19960


monthly_result = run_tool(
    "monthly_sales",
    {
        "month": "2011-11"
    }
)

assert monthly_result["success"] is True
assert monthly_result["data"][0]["revenue"] == 1509496.33


customer_result = run_tool(
    "customer_value",
    {
        "customer_id": 14646
    }
)

assert customer_result["success"] is True
assert customer_result["data"][0]["customer_id"] == 14646


product_result = run_tool(
    "product_performance",
    {
        "stock_code": "22423"
    }
)

assert product_result["success"] is True
assert product_result["data"][0]["stock_code"] == "22423"


segment_result = run_tool(
    "customer_segments",
    {
        "segment": "Champions"
    }
)

assert segment_result["success"] is True
assert segment_result["data"][0]["customer_count"] == 148


# ===============================
# Failed Tool Calls
# ===============================

unknown_tool = run_tool(
    "unknown_tool"
)

assert unknown_tool["success"] is False
assert unknown_tool["error_type"] == "ValueError"


invalid_month = run_tool(
    "monthly_sales",
    {
        "month": "2011/11"
    }
)

assert invalid_month["success"] is False
assert invalid_month["error_type"] == "ValueError"


invalid_arguments = run_tool(
    "sales_kpi",
    "invalid"
)

assert invalid_arguments["success"] is False
assert invalid_arguments["error_type"] == "TypeError"


print("Tool Router Test: PASS")