from src.query_service import (
    get_sales_kpi,
    get_monthly_sales,
    get_customer_value,
    get_product_performance,
    get_product_concentration,
    get_customer_segments
)


print("Sales KPI")
print("----------------")
for key, value in get_sales_kpi().items():
    print(f"{key}: {value}")


print("\nMonthly Sales")
print("----------------")
print(
    get_monthly_sales()
    .to_string(index=False)
)


print("\nCustomer Value")
print("----------------")
print(
    get_customer_value()
    .head(10)
    .to_string(index=False)
)


print("\nProduct Performance")
print("----------------")
print(
    get_product_performance()
    .head(10)
    .to_string(index=False)
)


print("\nProduct Concentration")
print("----------------")
print(
    get_product_concentration()
    .to_string(index=False)
)


print("\nCustomer Segments")
print("----------------")
print(
    get_customer_segments()
    .to_string(index=False)
)