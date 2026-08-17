import pandas as pd

from src.sales_analysis import calculate_sales_kpis


df = pd.read_csv(
    "data/processed/cleaned_sales.csv",
    dtype={
        "InvoiceNo": str,
        "StockCode": str
    }
)


kpis = calculate_sales_kpis(df)


print("Sales KPIs")
print("----------------")

for key, value in kpis.items():
    print(
        f"{key}: {value}"
    )