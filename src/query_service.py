import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "ecommerce.db"
SQL_DIR = PROJECT_ROOT / "database" / "sql"


def load_sql(filename):
    """读取正式业务SQL文件。"""
    sql_path = SQL_DIR / filename
    return sql_path.read_text(encoding="utf-8")


def get_connection():
    """创建SQLite连接。"""
    return sqlite3.connect(DB_PATH)


def get_sales_kpi():
    """返回整体销售KPI。"""
    query = load_sql("01_sales_kpis.sql")

    with get_connection() as conn:
        result = pd.read_sql_query(query, conn)

    data = result.iloc[0].to_dict()
    data["total_orders"] = int(data["total_orders"])
    data["total_quantity"] = int(data["total_quantity"])

    return data


def get_monthly_sales():
    """返回月度销售趋势与环比增长。"""
    query = load_sql("02_monthly_sales.sql")

    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_customer_value():
    """返回客户价值分析结果。"""
    query = load_sql("03_customer_value.sql")

    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_product_performance():
    """返回商品表现分析结果。"""
    query = load_sql("04_product_performance.sql")

    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_product_concentration():
    """返回商品收入集中度。"""
    query = load_sql("05_product_concentration.sql")

    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_customer_segments():
    """返回客户分群业务汇总。"""
    query = load_sql("09_business_queries.sql")

    with get_connection() as conn:
        return pd.read_sql_query(query, conn)