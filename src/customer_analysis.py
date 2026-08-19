def customer_revenue(df):
    """
    Calculate total revenue for each customer.
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