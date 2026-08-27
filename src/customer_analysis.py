def customer_revenue(df):
    """
    Calculate total revenue for each customer.
    计算每个客户的总消费金额
    """

    result = (
        df.groupby("CustomerID")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    return result

def customer_order_frequency(df):
    """
    Calculate the number of unique orders for each customer.
    计算每个客户的总订单数量
    """

    result = (
        df.groupby("CustomerID")["InvoiceNo"]
        .nunique()
        .sort_values(ascending=False)
    )

    return result

def customer_average_order_value(df):
    """
    Calculate average order value for each customer.
    计算每个客户的平均订单金额
    """

    revenue = (
        df.groupby("CustomerID")["Sales"].sum()
    )

    orders = (
        df.groupby("CustomerID")["InvoiceNo"].nunique()
    )

    result = (
        revenue / orders
    ).sort_values(ascending=False)

    return result