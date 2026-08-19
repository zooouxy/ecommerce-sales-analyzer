import pandas as pd

# 商品的销售额排名
def product_revenue(df):
    """
    Calculate total revenue for each product.
    """

    result = (
        df.groupby("Description")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    return result

# 商品的销量排名
def product_quantity(df):
    """
    Calculate total quantity sold for each product.
    """

    result = (
        df.groupby("Description")["Quantity"]
        .sum()
        .sort_values(ascending=False)
    )

    return result

# 商品的订单数/在多少订单中出现过
def product_order_count(df):
    """
    Calculate the number of unique orders containing each product.
    """

    result = (
        df.groupby("Description")["InvoiceNo"]
        .nunique()
        .sort_values(ascending=False)
    )

    return result