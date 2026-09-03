import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "ecommerce.db"
SQL_DIR = PROJECT_ROOT / "database" / "sql"


def load_sql(filename):
    """读取正式业务SQL文件。"""
    sql_path = SQL_DIR / filename

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    return sql_path.read_text(encoding="utf-8")


def get_connection():
    """创建SQLite数据库连接。"""
    return sqlite3.connect(DB_PATH)


def query_dataframe(filename):
    """执行SQL文件并返回DataFrame。"""
    query = load_sql(filename)

    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def dataframe_to_records(df):
    """将DataFrame转换为适合Tool和JSON返回的记录列表。"""
    clean_df = df.astype(object).where(pd.notna(df), None)
    return clean_df.to_dict(orient="records")


def validate_limit(limit):
    """校验Top N参数。"""
    if not isinstance(limit, int):
        raise TypeError("limit must be an integer")

    if limit <= 0:
        raise ValueError("limit must be greater than 0")


def get_sales_kpi():
    """返回整体销售KPI。"""
    result = query_dataframe("01_sales_kpis.sql")
    data = result.iloc[0].to_dict()

    data["total_orders"] = int(data["total_orders"])
    data["total_quantity"] = int(data["total_quantity"])

    return data


def validate_month(month):
    """校验月份参数，格式必须为YYYY-MM。"""
    if not isinstance(month, str):
        raise TypeError("month must be a string")

    try:
        parsed = pd.to_datetime(month, format="%Y-%m")
    except ValueError as exc:
        raise ValueError("month must use YYYY-MM format") from exc

    if parsed.strftime("%Y-%m") != month:
        raise ValueError("month must use YYYY-MM format")


def get_monthly_sales(month=None):
    """返回月度销售趋势，可按月份筛选。"""
    result = query_dataframe("02_monthly_sales.sql")

    if month is not None:
        validate_month(month)
        result = result[result["month"] == month]

    return dataframe_to_records(result)

def validate_customer_id(customer_id):
    """校验客户ID。"""
    if not isinstance(customer_id, int):
        raise TypeError("customer_id must be an integer")

    if customer_id <= 0:
        raise ValueError("customer_id must be greater than 0")


def get_customer_value(limit=None, customer_id=None):
    """返回客户价值分析结果，可按客户ID或Top N筛选。"""
    result = query_dataframe("03_customer_value.sql")

    if customer_id is not None:
        validate_customer_id(customer_id)
        result = result[result["customer_id"] == customer_id]

    if limit is not None:
        validate_limit(limit)
        result = result.head(limit)

    return dataframe_to_records(result)


def validate_stock_code(stock_code):
    """校验商品StockCode。"""
    if not isinstance(stock_code, str):
        raise TypeError("stock_code must be a string")

    stock_code = stock_code.strip().upper()

    if not stock_code:
        raise ValueError("stock_code must not be empty")

    return stock_code
def get_product_performance(limit=None, stock_code=None):
    """返回商品表现分析结果，可按StockCode或Top N筛选。"""
    result = query_dataframe("04_product_performance.sql")

    if stock_code is not None:
        stock_code = validate_stock_code(stock_code)
        result = result[result["stock_code"] == stock_code]

    if limit is not None:
        validate_limit(limit)
        result = result.head(limit)

    return dataframe_to_records(result)

def get_product_concentration():
    """返回商品收入集中度。"""
    result = query_dataframe("05_product_concentration.sql")
    data = result.astype(object).where(pd.notna(result), None)

    return data.iloc[0].to_dict()

VALID_SEGMENTS = {
    "Champions",
    "Loyal Customers",
    "Regular Customers",
    "High Value Lost",
    "Lost Customers",
    "At Risk",
    "Big Spenders"
}


def validate_segment(segment):
    """校验客户分群名称。"""
    if not isinstance(segment, str):
        raise TypeError("segment must be a string")

    segment = segment.strip()

    if segment not in VALID_SEGMENTS:
        raise ValueError(f"invalid segment: {segment}")

    return segment
def get_customer_segments(segment=None):
    """返回客户分群业务汇总，可按分群名称筛选。"""
    result = query_dataframe("09_business_queries.sql")

    if segment is not None:
        segment = validate_segment(segment)
        result = result[result["segment"] == segment]

    return dataframe_to_records(result)