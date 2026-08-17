import pandas as pd


def clean_sales_data(df):
    """
    Clean ecommerce transaction data.

    Parameters:
        df (pd.DataFrame):
            Raw transaction dataframe

    Returns:
        pd.DataFrame:
            Cleaned transaction dataframe
    """

    # Copy dataframe to avoid modifying original data
    df = df.copy()

    # Remove rows without product description
    df = df.dropna(subset=["Description"])

    # Remove cancelled orders and invalid quantities
    valid_quantity = df["Quantity"] > 0
    valid_unitprice = df["UnitPrice"] > 0
    df = df[
        valid_quantity &
        valid_unitprice
    ]

    # Calculate sales amount
    df["Sales"] = df["Quantity"] * df["UnitPrice"]

    return df