import pandas as pd

# 销售指标计算
def calculate_sales_kpis(df):
    """
    Calculate key sales performance indicators.

    Parameters:
        df:
            Cleaned sales dataframe

    Returns:
        dict:
            Sales KPIs
    """

    kpis = {}

    # Total revenue
    kpis["total_revenue"] = df["Sales"].sum()

    # Total orders
    kpis["total_orders"] = df["InvoiceNo"].nunique()

    # Total quantity sold
    kpis["total_quantity"] = df["Quantity"].sum()

    # Average order value
    kpis["average_order_value"] = (
        df["Sales"].sum()
        /
        df["InvoiceNo"].nunique()
    )

    return kpis