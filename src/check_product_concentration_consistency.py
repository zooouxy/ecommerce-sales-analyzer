import sqlite3
import pandas as pd

CSV_PATH = "data/processed/cleaned_sales.csv"
DB_PATH = "database/ecommerce.db"
SQL_PATH = "database/sql/05_product_concentration.sql"

EXCLUDED_STOCK_CODES = [
    "DOT",
    "POST",
    "M",
    "AMAZONFEE",
    "B",
    "C2",
    "23444",
    "BANK CHARGES",
    "23574",
    "S"
]


def prepare_product_data(df):
    """使用与数据库 ETL 相同的 StockCode 标准化规则。"""
    product_df = df.copy()

    product_df["StockCode"] = (
        product_df["StockCode"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    product_df = product_df[
        ~product_df["StockCode"].isin(EXCLUDED_STOCK_CODES)
        & product_df["Description"].notna()
    ].copy()

    return product_df


def build_pandas_product_revenue(df):
    """按标准化 StockCode 汇总商品收入。"""
    product_df = prepare_product_data(df)

    product_revenue = (
        product_df.groupby("StockCode", as_index=False)
        .agg(revenue=("Sales", "sum"))
    )

    product_revenue["revenue"] = product_revenue["revenue"].round(2)

    return product_revenue.sort_values(
        "revenue",
        ascending=False
    ).reset_index(drop=True)


def calculate_pandas_result(df):
    product_revenue = build_pandas_product_revenue(df)

    total_revenue = product_revenue["revenue"].sum()
    top10_revenue = product_revenue.head(10)["revenue"].sum()
    top10_share = top10_revenue / total_revenue * 100

    return product_revenue, {
        "total_product_revenue": round(total_revenue, 2),
        "top_10_revenue": round(top10_revenue, 2),
        "top_10_revenue_share_pct": round(top10_share, 2)
    }


def calculate_sql_result():
    """执行 SQL 商品集中度查询。"""
    with open(SQL_PATH, "r", encoding="utf-8") as file:
        sql = file.read()

    conn = sqlite3.connect(DB_PATH)

    try:
        result = pd.read_sql_query(sql, conn)
    finally:
        conn.close()

    return result.iloc[0].to_dict()


df = pd.read_csv(
    CSV_PATH,
    dtype={
        "InvoiceNo": str,
        "StockCode": str
    }
)

pandas_products, pandas_result = calculate_pandas_result(df)
sql_result = calculate_sql_result()

print("Pandas result:")
print(pandas_result)

print("\nSQL result:")
print(sql_result)

print("\nPandas Top 10:")
print(
    pandas_products[
        ["StockCode", "revenue"]
    ].head(10).to_string(index=False)
)

total_revenue_match = abs(
    pandas_result["total_product_revenue"]
    - sql_result["total_product_revenue"]
) <= 0.01

top10_revenue_match = abs(
    pandas_result["top_10_revenue"]
    - sql_result["top_10_revenue"]
) <= 0.01

share_match = (
    pandas_result["top_10_revenue_share_pct"]
    == sql_result["top_10_revenue_share_pct"]
)

print("\nProduct concentration reconciliation:")
print("Total revenue:", "PASS" if total_revenue_match else "FAIL")
print("Top 10 revenue:", "PASS" if top10_revenue_match else "FAIL")
print("Top 10 share:", "PASS" if share_match else "FAIL")

print(
    "\nResult:",
    "PASS"
    if total_revenue_match and top10_revenue_match and share_match
    else "FAIL"
)