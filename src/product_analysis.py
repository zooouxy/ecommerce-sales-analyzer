import pandas as pd

from src.business_rules import EXCLUDED_PRODUCT_STOCK_CODES


def prepare_product_data(df):
    """标准化商品编码并排除非商品交易。"""
    product_df = df.copy()

    product_df["StockCode"] = (
        product_df["StockCode"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    product_df = product_df[
        ~product_df["StockCode"].isin(EXCLUDED_PRODUCT_STOCK_CODES)
        & product_df["Description"].notna()
    ].copy()

    return product_df


def product_revenue(df):
    """按StockCode计算商品销售收入。"""
    product_df = prepare_product_data(df)

    return (
        product_df.groupby("StockCode")["Sales"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
    )


def product_quantity(df):
    """按StockCode计算商品销量。"""
    product_df = prepare_product_data(df)

    return (
        product_df.groupby("StockCode")["Quantity"]
        .sum()
        .sort_values(ascending=False)
    )


def product_order_count(df):
    """按StockCode计算商品出现的独立订单数。"""
    product_df = prepare_product_data(df)

    return (
        product_df.groupby("StockCode")["InvoiceNo"]
        .nunique()
        .sort_values(ascending=False)
    )


def analyze_product_performance(
    revenue_rank,
    quantity_rank,
    order_rank
):
    """汇总商品收入、销量、订单数和平均订单收入。"""
    product_analysis = pd.DataFrame({
        "Revenue": revenue_rank,
        "Quantity": quantity_rank,
        "Order_Count": order_rank
    })

    product_analysis["Average_Revenue_Per_Order"] = (
        product_analysis["Revenue"]
        / product_analysis["Order_Count"]
    ).round(2)

    return product_analysis.sort_values(
        "Revenue",
        ascending=False
    )


def analyze_product_concentration(product_revenue_data):
    """计算商品收入占比和Top 10商品收入集中度。"""
    if isinstance(product_revenue_data, pd.Series):
        product_revenue_df = (
            product_revenue_data
            .rename("Revenue")
            .to_frame()
        )
    else:
        product_revenue_df = product_revenue_data.copy()

    product_revenue_df["Revenue"] = (
        product_revenue_df["Revenue"]
        .round(2)
    )

    product_analysis = (
        product_revenue_df
        .sort_values(
            "Revenue",
            ascending=False
        )
        .copy()
    )

    total_revenue = product_analysis["Revenue"].sum()
    top10_revenue = product_analysis.head(10)["Revenue"].sum()
    top10_share = top10_revenue / total_revenue * 100

    product_analysis["Revenue_Percentage"] = (
        product_analysis["Revenue"]
        / total_revenue
        * 100
    )

    product_analysis["Cumulative_Revenue_Percentage"] = (
        product_analysis["Revenue_Percentage"]
        .cumsum()
    )

    return product_analysis, top10_share