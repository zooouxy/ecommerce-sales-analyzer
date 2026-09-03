from src.query_service import (
    get_sales_kpi,
    get_monthly_sales,
    get_customer_value,
    get_product_performance,
    get_product_concentration,
    get_customer_segments
)


def print_section(title, data, limit=None):
    print(f"\n{title}")
    print("-" * len(title))

    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{key}: {value}")
        return

    rows = data[:limit] if limit else data

    for row in rows:
        print(row)


def assert_raises(expected_exception, func, *args):
    """验证函数是否抛出预期异常。"""
    try:
        func(*args)
    except expected_exception:
        print(
            f"PASS: {func.__name__}{args} "
            f"raised {expected_exception.__name__}"
        )
        return

    raise AssertionError(
        f"{func.__name__}{args} did not raise "
        f"{expected_exception.__name__}"
    )


sales_kpi = get_sales_kpi()
monthly_sales = get_monthly_sales()
customer_value = get_customer_value()
product_performance = get_product_performance()
product_concentration = get_product_concentration()
customer_segments = get_customer_segments()


# ===============================
# Basic Query Tests
# ===============================

print_section("Sales KPI", sales_kpi)
print_section("Monthly Sales", monthly_sales)
print_section("Customer Value", customer_value, limit=10)
print_section("Product Performance", product_performance, limit=10)
print_section("Product Concentration", product_concentration)
print_section("Customer Segments", customer_segments)

assert isinstance(sales_kpi, dict)
assert isinstance(monthly_sales, list)
assert isinstance(customer_value, list)
assert isinstance(product_performance, list)
assert isinstance(product_concentration, dict)
assert isinstance(customer_segments, list)

assert round(
    product_concentration["top_10_revenue_share_pct"],
    2
) == 9.45

assert len(customer_segments) == 7


# ===============================
# Parameterized Query Tests
# ===============================

print("\nParameterized Query Tests")
print("-------------------------")

top_5_customers = get_customer_value(5)
top_3_products = get_product_performance(3)

assert len(top_5_customers) == 5
print("PASS: get_customer_value(5) returned 5 rows")

assert len(top_3_products) == 3
print("PASS: get_product_performance(3) returned 3 rows")


# ===============================
# Invalid Parameter Tests
# ===============================

print("\nInvalid Parameter Tests")
print("-----------------------")

assert_raises(
    ValueError,
    get_customer_value,
    0
)

assert_raises(
    ValueError,
    get_product_performance,
    -1
)

assert_raises(
    TypeError,
    get_customer_value,
    "5"
)

# ===============================
# Monthly Sales Parameter Tests
# ===============================

print("\nMonthly Sales Parameter Tests")
print("-----------------------------")

november_sales = get_monthly_sales("2011-11")

assert len(november_sales) == 1
assert november_sales[0]["month"] == "2011-11"
assert november_sales[0]["revenue"] == 1509496.33
assert november_sales[0]["orders"] == 2769
assert november_sales[0]["revenue_growth_pct"] == 30.69

print("PASS: get_monthly_sales('2011-11') returned correct result")

missing_month = get_monthly_sales("2012-01")

assert missing_month == []

print("PASS: get_monthly_sales('2012-01') returned empty result")


assert_raises(
    ValueError,
    get_monthly_sales,
    "2011/11"
)

assert_raises(
    TypeError,
    get_monthly_sales,
    201111
)

# ===============================
# Customer Value Parameter Tests
# ===============================

print("\nCustomer Value Parameter Tests")
print("------------------------------")

customer = get_customer_value(customer_id=14646)

assert len(customer) == 1
assert customer[0]["customer_id"] == 14646
assert customer[0]["total_orders"] == 73
assert customer[0]["total_revenue"] == 280206.02
assert customer[0]["average_order_value"] == 3838.44

print("PASS: get_customer_value(customer_id=14646) returned correct result")

missing_customer = get_customer_value(customer_id=99999)

assert missing_customer == []

print("PASS: get_customer_value(customer_id=99999) returned empty result")

assert_raises(
    TypeError,
    get_customer_value,
    None,
    "14646"
)

assert_raises(
    ValueError,
    get_customer_value,
    None,
    0
)

# ===============================
# Product Performance Parameter Tests
# ===============================

print("\nProduct Performance Parameter Tests")
print("-----------------------------------")

product = get_product_performance(stock_code="22423")

assert len(product) == 1
assert product[0]["stock_code"] == "22423"
assert product[0]["description"] == "REGENCY CAKESTAND 3 TIER"
assert product[0]["revenue"] == 174484.74
assert product[0]["quantity"] == 13879
assert product[0]["orders"] == 1988

print("PASS: get_product_performance(stock_code='22423') returned correct result")

normalized_product = get_product_performance(stock_code=" 22423 ")

assert len(normalized_product) == 1
assert normalized_product[0]["stock_code"] == "22423"

print("PASS: stock_code normalization works")

missing_product = get_product_performance(stock_code="XXXXX")

assert missing_product == []

print("PASS: get_product_performance(stock_code='XXXXX') returned empty result")

assert_raises(
    TypeError,
    get_product_performance,
    None,
    22423
)

assert_raises(
    ValueError,
    get_product_performance,
    None,
    "   "
)

# ===============================
# Customer Segment Parameter Tests
# ===============================

print("\nCustomer Segment Parameter Tests")
print("--------------------------------")

champions = get_customer_segments("Champions")

assert len(champions) == 1
assert champions[0]["segment"] == "Champions"
assert champions[0]["customer_count"] == 148
assert champions[0]["total_revenue"] == 3218123.84
assert champions[0]["revenue_percentage"] == 36.11
assert champions[0]["average_revenue_per_customer"] == 21744.08

print("PASS: get_customer_segments('Champions') returned correct result")

assert_raises(
    ValueError,
    get_customer_segments,
    "VIP"
)

assert_raises(
    TypeError,
    get_customer_segments,
    123
)
print("\nQuery Service Test: PASS")