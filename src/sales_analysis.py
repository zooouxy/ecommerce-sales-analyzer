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
        df["Sales"].sum() / df["InvoiceNo"].nunique()
    )

    return kpis

# 月度销售趋势分析
def monthly_sales_trend(df):
    """
    Calculate monthly sales revenue trend.

    Parameters:
        df:
            Cleaned sales dataframe

    Returns:
        pandas.Series:
            Monthly revenue
    """

    monthly_sales = (
        df.groupby(
            df["InvoiceDate"].dt.to_period("M")
        )["Sales"].sum()
    )

    return monthly_sales

# 商品销售额排行
def top_products_by_revenue(df, n=10):
    """
    Return top products by revenue.

    Parameters:
        df:
            Cleaned sales dataframe

        n:
            Number of products

    Returns:
        pandas.Series
    """

    products = (
        df.groupby("Description")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(n)
    )

    return products

# 国家销售排行
def sales_by_country(df):
    """
    Calculate revenue by country.

    Returns:
        pandas.Series
    """

    country_sales = (
        df
        .groupby("Country")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    return country_sales