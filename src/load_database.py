import sqlite3
from pathlib import Path

import pandas as pd
import os
from database import create_database

# 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 输入数据路径
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"

# SQLite 数据库路径
DATABASE_PATH = PROJECT_ROOT / "database" / "ecommerce.db"

DB_PATH = "database/ecommerce.db"
SCHEMA_PATH = "database/schema.sql"
VIEW_DIR = "database/views"
def load_source_data():
    """
    读取清洗后的交易数据。
    """

    df = pd.read_csv(
        DATA_PATH,
        dtype={
            # 订单编号和商品编号是业务标识符，不参与数值计算
            "InvoiceNo": str,
            "StockCode": str
        }
    )

    # 将订单日期转换成真正的 datetime 类型
    # errors="coerce" 表示无法解析的日期转换成 NaT
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    )

    return df

def transform_customers(df):
    """
    从交易明细中生成客户维度表。

    一个客户可能出现在很多交易记录中，
    因此这里需要去重，最终每个 CustomerID 只保留一条客户记录。
    """

    customers = (
        df[["CustomerID", "Country"]]
        .dropna(subset=["CustomerID"])
        .drop_duplicates(subset=["CustomerID"])
        .copy()
    )

    # CustomerID 在 CSV 中因为缺失值被 Pandas 读取成 float。
    # 数据库设计中 CustomerID 是整数型业务标识，因此转换成整数。
    customers["CustomerID"] = (
        customers["CustomerID"]
        .astype(int)
    )

    return customers


def transform_products(df):
    """
    生成商品维度表。

    处理规则：
    1. 标准化 StockCode
    2. 标准化 Description
    3. 统计每个商品描述的出现次数
    4. 为每个 StockCode 选择出现次数最多的描述
    """

    products_source = (
        df[["StockCode", "Description"]]
        .dropna(subset=["StockCode", "Description"])
        .copy()
    )

    # 标准化商品编码
    # 去除前后空格并统一大写，避免 84997A / 84997a 被识别为两个商品
    products_source["StockCode"] = (
        products_source["StockCode"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # 标准化商品描述
    # 去除前后空格、压缩连续空格，并统一大写
    products_source["Description"] = (
        products_source["Description"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
    )

    # 统计每个 StockCode + Description 组合出现次数
    description_counts = (
        products_source
        .groupby(
            ["StockCode", "Description"]
        )
        .size()
        .reset_index(
            name="Row_Count"
        )
    )

    # 按商品编码分组，
    # 对每个商品选择出现次数最多的描述
    products = (
        description_counts
        .sort_values(
            ["StockCode", "Row_Count"],
            ascending=[True, False]
        )
        .drop_duplicates(
            subset=["StockCode"]
        )
        [["StockCode", "Description"]]
        .reset_index(drop=True)
    )

    return products

def transform_orders(df):
    """
    从交易明细生成订单主表。

    一个 InvoiceNo 对应一个 Order。
    """

    orders = (
        df.groupby("InvoiceNo")
        .agg(
            # 同一订单可能有多个商品明细时间
            # 取最早时间作为订单时间
            InvoiceDate=("InvoiceDate", "min"),

            # 同一个订单已经验证过只有一个 CustomerID
            CustomerID=("CustomerID", "first"),
        )
        .reset_index()
    )

    # 生成数据库内部订单主键
    orders.insert(
        0,
        "OrderID",
        range(1, len(orders) + 1)
    )

    return orders

def transform_order_items(
    df,
    orders,
):
    """
    从交易明细生成订单商品明细表。

    一条 CSV 记录对应一条 order_item。
    """

    order_items = df[
        [
            "InvoiceNo",
            "StockCode",
            "Quantity",
            "UnitPrice",
            "Sales"
        ]
    ].copy()

    # 标准化商品编码
    # 必须与 products 表使用完全相同的规则
    order_items["StockCode"] = (
        order_items["StockCode"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # 建立 InvoiceNo -> OrderID 的映射
    invoice_to_order = (
        orders.set_index("InvoiceNo")["OrderID"]
    )

    # 根据 InvoiceNo 找到对应的 OrderID
    order_items["OrderID"] = (
        order_items["InvoiceNo"]
        .map(invoice_to_order)
    )

    # 生成数据库内部的订单商品明细主键
    order_items.insert(
        0,
        "TransactionID",
        range(1, len(order_items) + 1)
    )

    # 删除原始业务订单号
    # 数据库中通过 OrderID 与 orders 建立关系
    order_items = order_items.drop(
        columns=["InvoiceNo"]
    )

    return order_items

def prepare_for_database(
    customers,
    products,
    orders,
    order_items
):
    """
    将分析阶段使用的列名统一转换为数据库 Schema 使用的列名。
    """

    # 客户表：转换为数据库命名规范
    customers = customers.rename(
        columns={
            "CustomerID": "customer_id",
            "Country": "country"
        }
    )
    # CustomerID 不允许为空，因此转换为普通整数
    customers["customer_id"] = (
        customers["customer_id"].astype(int)
    )

    # 商品表
    products = products.rename(
        columns={
            "StockCode": "stock_code",
            "Description": "description"
        }
    )

    # 订单表
    orders = orders.rename(
        columns={
            "OrderID": "order_id",
            "InvoiceNo": "invoice_no",
            "InvoiceDate": "invoice_date",
            "CustomerID": "customer_id"
        }
    )
    # CustomerID 允许缺失，因此使用 Pandas 的可空整数类型
    orders["customer_id"] = (
        orders["customer_id"].astype("Int64")
    )

    # 订单商品明细表
    order_items = order_items.rename(
        columns={
            "TransactionID": "transaction_id",
            "OrderID": "order_id",
            "StockCode": "stock_code",
            "Quantity": "quantity",
            "UnitPrice": "unit_price",
            "Sales": "sales"
        }
    )

    return (
        customers,
        products,
        orders,
        order_items
    )

def load_to_database(
    customers,
    products,
    orders,
    order_items
):
    """
    将转换后的四张表写入 SQLite 数据库。

    写入顺序：
    customers
    products
    orders
    order_items

    这样可以满足外键依赖关系。
    """

    # 建立数据库连接
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:
        # 开启 SQLite 外键约束
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        # 使用数据库事务统一提交
        with connection:

            # 先写入客户表
            customers.to_sql(
                "customers",
                connection,
                if_exists="append",
                index=False
            )

            # 再写入商品表
            products.to_sql(
                "products",
                connection,
                if_exists="append",
                index=False
            )

            # 写入订单表
            orders.to_sql(
                "orders",
                connection,
                if_exists="append",
                index=False
            )

            # 最后写入订单商品明细表
            order_items.to_sql(
                "order_items",
                connection,
                if_exists="append",
                index=False
            )

    finally:
        # 关闭数据库连接
        connection.close()

    print("Data loaded successfully.")
def load_views(conn):
    """
    自动加载 database/views 下所有 SQL View 文件。
    """

    if not os.path.exists(VIEW_DIR):
        print("View directory not found.")
        return

    view_files = sorted(
        [
            f for f in os.listdir(VIEW_DIR)
            if f.endswith(".sql")
        ]
    )

    for file in view_files:
        path = os.path.join(VIEW_DIR, file)

        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        try:
            conn.executescript(sql)
            print(f"Loaded view: {file}")

        except Exception as e:
            print(f"Failed view: {file}")
            raise e
def reset_database():
    """
    删除现有 SQLite 数据库文件，
    为一次完整 ETL 创建干净环境。
    """

    # 如果数据库文件存在，则删除
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    # 重新创建数据库和 Schema
    # 这里直接复用我们之前的 create_database()
    create_database()
if __name__ == "__main__":
    # 重新初始化数据库
    reset_database()

    # 读取源数据
    df = load_source_data()

    # Transform（转换）
    customers = transform_customers(df)
    products = transform_products(df)
    orders = transform_orders(df)
    order_items = transform_order_items(
        df,
        orders
    )

    # 验证转换结果
    print("Transaction rows:", len(df))
    print("Customer rows:", len(customers))
    print("Product rows:", len(products))
    print("Order rows:", len(orders))
    print("Order item rows:", len(order_items))

    print(
        "Missing OrderID:",
        order_items["OrderID"].isna().sum()
    )

    print(
        "Duplicate TransactionID:",
        order_items["TransactionID"].duplicated().sum()
    )

    product_codes = set(
        products["StockCode"]
    )

    missing_products = (
        ~order_items["StockCode"]
        .isin(product_codes)
    ).sum()

    print(
        "Missing Product:",
        missing_products
    )

    # 将 ETL 结果转换为数据库字段命名
    customers, products, orders, order_items = (
        prepare_for_database(
            customers,
            products,
            orders,
            order_items
        )
    )

    # Load（加载）到 SQLite
    load_to_database(
        customers,
        products,
        orders,
        order_items
    )

    # 创建分析 Views
    conn = sqlite3.connect(DATABASE_PATH)

    load_views(conn)
    print("Views created successfully.")
    conn.close()