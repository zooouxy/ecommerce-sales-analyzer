import sqlite3
from pathlib import Path


# 获取项目根目录
# __file__ 是当前 database.py 的路径
# parent.parent 可以回到项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 数据库文件路径
DATABASE_PATH = PROJECT_ROOT / "database" / "ecommerce.db"

# Schema 文件路径
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


def create_database():
    """
    创建 SQLite 数据库，并执行 schema.sql。
    """

    # 连接 SQLite 数据库
    # 如果数据库文件不存在，SQLite 会自动创建
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        # SQLite 默认不会强制执行外键约束
        # 显式开启外键约束，保证数据关系完整性
        connection.execute("PRAGMA foreign_keys = ON")

        # 读取数据库 Schema 文件
        with open(
            SCHEMA_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            schema = file.read()

        # 一次执行整个 Schema
        connection.executescript(schema)

        # 提交数据库结构变化
        connection.commit()

        print("Database created successfully.")

    finally:
        # 无论成功还是失败，都关闭数据库连接
        connection.close()


if __name__ == "__main__":
    create_database()