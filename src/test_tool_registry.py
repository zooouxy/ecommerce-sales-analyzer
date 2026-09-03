from src.tool_registry import (
    TOOL_REGISTRY,
    get_tool,
    execute_tool,
    get_function_schemas
)


assert len(TOOL_REGISTRY) == 6

assert "sales_kpi" in TOOL_REGISTRY
assert "monthly_sales" in TOOL_REGISTRY
assert "customer_value" in TOOL_REGISTRY
assert "product_performance" in TOOL_REGISTRY
assert "product_concentration" in TOOL_REGISTRY
assert "customer_segments" in TOOL_REGISTRY


sales_tool = get_tool("sales_kpi")

assert sales_tool["description"]
assert sales_tool["parameters"] == {}


sales_result = execute_tool("sales_kpi")

assert sales_result["total_orders"] == 19960


monthly_result = execute_tool(
    "monthly_sales",
    month="2011-11"
)

assert monthly_result[0]["revenue"] == 1509496.33


customer_result = execute_tool(
    "customer_value",
    customer_id=14646
)

assert customer_result[0]["customer_id"] == 14646


product_result = execute_tool(
    "product_performance",
    stock_code="22423"
)

assert product_result[0]["stock_code"] == "22423"


segment_result = execute_tool(
    "customer_segments",
    segment="Champions"
)

assert segment_result[0]["customer_count"] == 148


try:
    get_tool("unknown_tool")
    raise AssertionError("Expected ValueError")
except ValueError:
    pass

schemas = get_function_schemas()

assert len(schemas) == 6

monthly_schema = next(
    schema
    for schema in schemas
    if schema["name"] == "monthly_sales"
)

assert monthly_schema["type"] == "function"
assert monthly_schema["name"] == "monthly_sales"
assert monthly_schema["strict"] is True

assert (
    monthly_schema["parameters"]
    ["properties"]["month"]["type"]
    == "string"
)

assert (
    monthly_schema["parameters"]
    ["additionalProperties"]
    is False
)

print("PASS: Responses API function schemas generated correctly")

print("Tool Registry Test: PASS")