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

def analyze_monthly_sales(monthly_sales):
    """
    分析月度销售趋势，计算月度增长率并找出销售峰值月份。
    """

    # 计算环比增长率
    # pct_change() 会计算当前月份相对于上一个月份的变化比例
    monthly_growth = monthly_sales.pct_change() * 100

    # 找出销售额最高的月份
    peak_month = monthly_sales.idxmax()

    # 找出销售额最高值
    peak_revenue = monthly_sales.max()

    # 将分析结果整理成字典
    monthly_analysis = {
        "monthly_growth": monthly_growth,
        "peak_month": peak_month,
        "peak_revenue": peak_revenue
    }

    return monthly_analysis


def analyze_country_sales(country_sales):
    """
    分析不同国家的销售贡献。

    Parameters:
        country_sales:
            按国家汇总后的销售额 Series

    Returns:
        pandas.DataFrame:
            包含销售额和收入占比
    """

    # 将 Series 转换成 DataFrame，方便添加新增列
    country_analysis = country_sales.to_frame(
        name="Total_Revenue"
    )

    # 计算全部国家总销售额
    total_revenue = (
        country_analysis["Total_Revenue"]
        .sum()
    )

    # 计算每个国家收入占比
    country_analysis["Revenue_Percentage"] = (
            country_analysis["Total_Revenue"]
            /
            total_revenue
            *
            100
    )

    # 按收入从高到低排序
    country_analysis = country_analysis.sort_values(
        "Total_Revenue",
        ascending=False
    )

    return country_analysis


