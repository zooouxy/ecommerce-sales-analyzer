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


def get_data_coverage():
    """返回订单数据覆盖的起止时间。"""
    result = query_dataframe("10_data_coverage.sql")

    if result.empty:
        return {
            "data_start_date": None,
            "data_end_date": None
        }

    return dataframe_to_records(result)[0]


def dataframe_row_to_record(df, index):
    """将DataFrame指定行转换为JSON友好的记录。"""
    return dataframe_to_records(df.loc[[index]])[0]


def add_revenue_change_semantics(record):
    """为月度记录补充收入变化方向和变化幅度。"""
    if record is None:
        return None

    growth = record.get("revenue_growth_pct")

    if growth is None:
        record["revenue_change_direction"] = None
        record["revenue_change_magnitude_pct"] = None
        return record

    if growth > 0:
        direction = "increase"
    elif growth < 0:
        direction = "decrease"
    else:
        direction = "flat"

    record["revenue_change_direction"] = direction
    record["revenue_change_magnitude_pct"] = abs(growth)

    return record


def get_complete_month_mask(result, data_start_date, data_end_date):
    """判断月度记录是否覆盖完整自然月。"""
    month_dates = pd.to_datetime(result["month"], format="%Y-%m")
    start_date = pd.to_datetime(data_start_date)
    end_date = pd.to_datetime(data_end_date)

    first_month = start_date.to_period("M")
    last_month = end_date.to_period("M")

    first_month_complete = start_date.day == 1
    last_month_complete = (
        end_date.normalize()
        == (end_date + pd.offsets.MonthEnd(0)).normalize()
    )

    month_periods = month_dates.dt.to_period("M")
    mask = pd.Series(True, index=result.index)

    if not first_month_complete:
        mask &= month_periods != first_month

    if not last_month_complete:
        mask &= month_periods != last_month

    return mask


def get_monthly_sales_with_completeness():
    """加载月度销售数据，并统一补充完整月份标记。"""
    result = query_dataframe("02_monthly_sales.sql")
    coverage = get_data_coverage()

    if result.empty:
        return result, coverage

    result = result.sort_values("month").reset_index(drop=True)

    result["is_complete_month"] = get_complete_month_mask(
        result,
        coverage["data_start_date"],
        coverage["data_end_date"]
    )

    return result, coverage


def get_monthly_trend_insights():
    """返回基于完整月份比较的月度销售关键趋势洞察。"""
    result, coverage = get_monthly_sales_with_completeness()

    if result.empty:
        return {
            "data_start_date": coverage["data_start_date"],
            "data_end_date": coverage["data_end_date"],
            "highest_revenue_month": None,
            "highest_order_month": None,
            "largest_revenue_growth_month": None,
            "largest_revenue_decline_month": None,
            "latest_month": None
        }

    complete_months = result[result["is_complete_month"]]

    highest_revenue = None
    highest_order = None

    if not complete_months.empty:
        highest_revenue_index = complete_months["revenue"].idxmax()
        highest_order_index = complete_months["orders"].idxmax()

        highest_revenue = dataframe_row_to_record(
            result,
            highest_revenue_index
        )
        highest_order = dataframe_row_to_record(
            result,
            highest_order_index
        )

    result["previous_month_complete"] = result[
        "is_complete_month"
    ].shift(1, fill_value=False)

    growth_data = result[
        result["is_complete_month"]
        & result["previous_month_complete"]
        & result["revenue_growth_pct"].notna()
    ]

    positive_growth = growth_data[
        growth_data["revenue_growth_pct"] > 0
    ]
    negative_growth = growth_data[
        growth_data["revenue_growth_pct"] < 0
    ]

    largest_growth = None

    if not positive_growth.empty:
        largest_growth_index = positive_growth[
            "revenue_growth_pct"
        ].idxmax()
        largest_growth = dataframe_row_to_record(
            result,
            largest_growth_index
        )

    largest_decline = None

    if not negative_growth.empty:
        largest_decline_index = negative_growth[
            "revenue_growth_pct"
        ].idxmin()
        largest_decline = dataframe_row_to_record(
            result,
            largest_decline_index
        )

    latest_index = result.index[-1]
    latest_month = dataframe_row_to_record(result, latest_index)
    latest_month["is_partial_month"] = not bool(
        result.loc[latest_index, "is_complete_month"]
    )

    for record in (
        highest_revenue,
        highest_order,
        largest_growth,
        largest_decline,
        latest_month
    ):
        if record is not None:
            record.pop("is_complete_month", None)
            record.pop("previous_month_complete", None)
            add_revenue_change_semantics(record)

    return {
        "data_start_date": coverage["data_start_date"],
        "data_end_date": coverage["data_end_date"],
        "highest_revenue_month": highest_revenue,
        "highest_order_month": highest_order,
        "largest_revenue_growth_month": largest_growth,
        "largest_revenue_decline_month": largest_decline,
        "latest_month": latest_month
    }


def calculate_percentage_difference(left_value, right_value):
    """计算right相对left的百分比变化。"""
    if left_value == 0:
        return None

    return round(
        (right_value - left_value) * 100.0 / left_value,
        2
    )


def get_higher_month(
    left_month,
    left_value,
    right_month,
    right_value
):
    """返回指定指标数值更高的月份，相等时返回None。"""
    if left_value > right_value:
        return left_month

    if right_value > left_value:
        return right_month

    return None


def get_higher_entity(
    left_entity,
    left_value,
    right_entity,
    right_value
):
    """返回指定指标数值更高的实体，相等时返回None。"""
    if left_value > right_value:
        return left_entity

    if right_value > left_value:
        return right_entity

    return None


def get_difference_direction(value):
    """根据有符号差值返回变化方向。"""
    if value > 0:
        return "increase"

    if value < 0:
        return "decrease"

    return "flat"


def build_difference_semantics(difference, difference_pct):
    """为比较差值补充方向和绝对变化幅度。"""
    return {
        "direction": get_difference_direction(difference),
        "magnitude": abs(difference),
        "magnitude_pct": (
            None
            if difference_pct is None
            else abs(difference_pct)
        )
    }


def build_point_difference_semantics(difference_pp):
    """为占比百分点差异补充方向和绝对幅度。"""
    return {
        "direction": get_difference_direction(difference_pp),
        "magnitude_pp": abs(difference_pp)
    }


def get_month_comparison(month_a, month_b):
    """比较两个指定月份的销售表现。"""
    validate_month(month_a)
    validate_month(month_b)

    if month_a == month_b:
        raise ValueError("month_a and month_b must be different")

    result, coverage = get_monthly_sales_with_completeness()

    left_df = result[result["month"] == month_a]
    right_df = result[result["month"] == month_b]

    missing_months = []

    if left_df.empty:
        missing_months.append(month_a)

    if right_df.empty:
        missing_months.append(month_b)

    if missing_months:
        return {
            "entity_type": "month",
            "month_a": month_a,
            "month_b": month_b,
            "left": None,
            "right": None,
            "comparison": None,
            "comparison_is_fully_comparable": False,
            "partial_months": [],
            "missing_months": missing_months
        }

    left_index = left_df.index[0]
    right_index = right_df.index[0]

    left = dataframe_row_to_record(result, left_index)
    right = dataframe_row_to_record(result, right_index)

    left_complete = bool(
        result.loc[left_index, "is_complete_month"]
    )
    right_complete = bool(
        result.loc[right_index, "is_complete_month"]
    )

    left["is_partial_month"] = not left_complete
    right["is_partial_month"] = not right_complete

    left.pop("is_complete_month", None)
    right.pop("is_complete_month", None)

    add_revenue_change_semantics(left)
    add_revenue_change_semantics(right)

    revenue_difference = round(
        right["revenue"] - left["revenue"],
        2
    )
    revenue_difference_pct = calculate_percentage_difference(
        left["revenue"],
        right["revenue"]
    )

    orders_difference = int(
        right["orders"] - left["orders"]
    )
    orders_difference_pct = calculate_percentage_difference(
        left["orders"],
        right["orders"]
    )

    comparison = {
        "revenue_difference": revenue_difference,
        "revenue_difference_pct": revenue_difference_pct,
        "revenue_difference_semantics": build_difference_semantics(
            revenue_difference,
            revenue_difference_pct
        ),
        "orders_difference": orders_difference,
        "orders_difference_pct": orders_difference_pct,
        "orders_difference_semantics": build_difference_semantics(
            orders_difference,
            orders_difference_pct
        ),
        "higher_revenue_month": get_higher_month(
            month_a,
            left["revenue"],
            month_b,
            right["revenue"]
        ),
        "higher_order_month": get_higher_month(
            month_a,
            left["orders"],
            month_b,
            right["orders"]
        )
    }

    partial_months = []

    if left["is_partial_month"]:
        partial_months.append(month_a)

    if right["is_partial_month"]:
        partial_months.append(month_b)

    return {
        "entity_type": "month",
        "month_a": month_a,
        "month_b": month_b,
        "left": left,
        "right": right,
        "comparison": comparison,
        "comparison_is_fully_comparable": (
            left_complete
            and right_complete
        ),
        "partial_months": partial_months,
        "missing_months": [],
        "data_start_date": coverage["data_start_date"],
        "data_end_date": coverage["data_end_date"]
    }


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


def get_product_comparison(stock_code_a, stock_code_b):
    """比较两个指定商品的销售表现。"""
    stock_code_a = validate_stock_code(stock_code_a)
    stock_code_b = validate_stock_code(stock_code_b)

    if stock_code_a == stock_code_b:
        raise ValueError(
            "stock_code_a and stock_code_b must be different"
        )

    result = query_dataframe("04_product_performance.sql")

    left_df = result[result["stock_code"] == stock_code_a]
    right_df = result[result["stock_code"] == stock_code_b]

    missing_stock_codes = []

    if left_df.empty:
        missing_stock_codes.append(stock_code_a)

    if right_df.empty:
        missing_stock_codes.append(stock_code_b)

    if missing_stock_codes:
        return {
            "entity_type": "product",
            "stock_code_a": stock_code_a,
            "stock_code_b": stock_code_b,
            "left": None,
            "right": None,
            "comparison": None,
            "missing_stock_codes": missing_stock_codes
        }

    left = dataframe_to_records(left_df.iloc[[0]])[0]
    right = dataframe_to_records(right_df.iloc[[0]])[0]

    revenue_difference = round(
        right["revenue"] - left["revenue"],
        2
    )
    revenue_difference_pct = calculate_percentage_difference(
        left["revenue"],
        right["revenue"]
    )

    quantity_difference = int(
        right["quantity"] - left["quantity"]
    )
    quantity_difference_pct = calculate_percentage_difference(
        left["quantity"],
        right["quantity"]
    )

    orders_difference = int(
        right["orders"] - left["orders"]
    )
    orders_difference_pct = calculate_percentage_difference(
        left["orders"],
        right["orders"]
    )

    comparison = {
        "revenue_difference": revenue_difference,
        "revenue_difference_pct": revenue_difference_pct,
        "revenue_difference_semantics": build_difference_semantics(
            revenue_difference,
            revenue_difference_pct
        ),
        "quantity_difference": quantity_difference,
        "quantity_difference_pct": quantity_difference_pct,
        "quantity_difference_semantics": build_difference_semantics(
            quantity_difference,
            quantity_difference_pct
        ),
        "orders_difference": orders_difference,
        "orders_difference_pct": orders_difference_pct,
        "orders_difference_semantics": build_difference_semantics(
            orders_difference,
            orders_difference_pct
        ),
        "higher_revenue_product": get_higher_entity(
            stock_code_a,
            left["revenue"],
            stock_code_b,
            right["revenue"]
        ),
        "higher_quantity_product": get_higher_entity(
            stock_code_a,
            left["quantity"],
            stock_code_b,
            right["quantity"]
        ),
        "higher_order_product": get_higher_entity(
            stock_code_a,
            left["orders"],
            stock_code_b,
            right["orders"]
        )
    }

    return {
        "entity_type": "product",
        "stock_code_a": stock_code_a,
        "stock_code_b": stock_code_b,
        "left": left,
        "right": right,
        "comparison": comparison,
        "missing_stock_codes": []
    }


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


def get_segment_comparison(segment_a, segment_b):
    """比较两个指定客户分群的业务表现。"""
    segment_a = validate_segment(segment_a)
    segment_b = validate_segment(segment_b)

    if segment_a == segment_b:
        raise ValueError(
            "segment_a and segment_b must be different"
        )

    result = query_dataframe("09_business_queries.sql")

    left_df = result[result["segment"] == segment_a]
    right_df = result[result["segment"] == segment_b]

    missing_segments = []

    if left_df.empty:
        missing_segments.append(segment_a)

    if right_df.empty:
        missing_segments.append(segment_b)

    if missing_segments:
        return {
            "entity_type": "customer_segment",
            "segment_a": segment_a,
            "segment_b": segment_b,
            "left": None,
            "right": None,
            "comparison": None,
            "missing_segments": missing_segments
        }

    left = dataframe_to_records(left_df.iloc[[0]])[0]
    right = dataframe_to_records(right_df.iloc[[0]])[0]

    customer_count_difference = int(
        right["customer_count"] - left["customer_count"]
    )
    customer_count_difference_pct = calculate_percentage_difference(
        left["customer_count"],
        right["customer_count"]
    )

    total_revenue_difference = round(
        right["total_revenue"] - left["total_revenue"],
        2
    )
    total_revenue_difference_pct = calculate_percentage_difference(
        left["total_revenue"],
        right["total_revenue"]
    )

    revenue_percentage_difference_pp = round(
        right["revenue_percentage"] - left["revenue_percentage"],
        2
    )

    average_revenue_difference = round(
        right["average_revenue_per_customer"]
        - left["average_revenue_per_customer"],
        2
    )
    average_revenue_difference_pct = calculate_percentage_difference(
        left["average_revenue_per_customer"],
        right["average_revenue_per_customer"]
    )

    comparison = {
        "customer_count_difference": customer_count_difference,
        "customer_count_difference_pct": customer_count_difference_pct,
        "customer_count_difference_semantics": build_difference_semantics(
            customer_count_difference,
            customer_count_difference_pct
        ),
        "total_revenue_difference": total_revenue_difference,
        "total_revenue_difference_pct": total_revenue_difference_pct,
        "total_revenue_difference_semantics": build_difference_semantics(
            total_revenue_difference,
            total_revenue_difference_pct
        ),
        "revenue_percentage_difference_pp": (
            revenue_percentage_difference_pp
        ),
        "revenue_percentage_difference_semantics": (
            build_point_difference_semantics(
                revenue_percentage_difference_pp
            )
        ),
        "average_revenue_per_customer_difference": (
            average_revenue_difference
        ),
        "average_revenue_per_customer_difference_pct": (
            average_revenue_difference_pct
        ),
        "average_revenue_per_customer_difference_semantics": (
            build_difference_semantics(
                average_revenue_difference,
                average_revenue_difference_pct
            )
        ),
        "higher_customer_count_segment": get_higher_entity(
            segment_a,
            left["customer_count"],
            segment_b,
            right["customer_count"]
        ),
        "higher_total_revenue_segment": get_higher_entity(
            segment_a,
            left["total_revenue"],
            segment_b,
            right["total_revenue"]
        ),
        "higher_revenue_percentage_segment": get_higher_entity(
            segment_a,
            left["revenue_percentage"],
            segment_b,
            right["revenue_percentage"]
        ),
        "higher_average_revenue_per_customer_segment": get_higher_entity(
            segment_a,
            left["average_revenue_per_customer"],
            segment_b,
            right["average_revenue_per_customer"]
        )
    }

    return {
        "entity_type": "customer_segment",
        "segment_a": segment_a,
        "segment_b": segment_b,
        "left": left,
        "right": right,
        "comparison": comparison,
        "missing_segments": []
    }