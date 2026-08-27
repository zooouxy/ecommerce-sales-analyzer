import sqlite3
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "ecommerce.db"


def configure_stdout():
    """让Windows终端尽量使用UTF-8输出。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def run_sql(sql_path):
    """执行SQL文件并打印查询结果。"""
    sql_file = PROJECT_ROOT / sql_path

    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file}")

    sql = sql_file.read_text(encoding="utf-8")

    conn = sqlite3.connect(DB_PATH)

    try:
        result = pd.read_sql_query(sql, conn)
        print(result.to_string(index=False))
    finally:
        conn.close()


if __name__ == "__main__":
    configure_stdout()

    if len(sys.argv) != 2:
        print("Usage: python tools/run_sql.py <sql_file>")
        sys.exit(1)

    run_sql(sys.argv[1])