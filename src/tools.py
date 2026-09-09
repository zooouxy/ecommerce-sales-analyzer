from src.query_service import (
    get_customer_segments,
    get_customer_value,
    get_month_comparison,
    get_monthly_sales,
    get_monthly_trend_insights,
    get_product_comparison,
    get_product_concentration,
    get_product_performance,
    get_sales_kpi,
    get_segment_comparison
)


def sales_kpi_tool():
    """获取整体销售KPI。"""
    return get_sales_kpi()


def monthly_sales_tool(month=None):
    """获取月度销售数据，可按YYYY-MM筛选。"""
    return get_monthly_sales(month=month)


def monthly_trend_insights_tool():
    """获取基于完整月份比较的月度销售关键趋势洞察。"""
    return get_monthly_trend_insights()


def month_comparison_tool(month_a, month_b):
    """比较两个指定月份的销售表现。"""
    return get_month_comparison(
        month_a=month_a,
        month_b=month_b
    )


def customer_value_tool(limit=None, customer_id=None):
    """获取客户价值数据，可查询Top N或指定客户。"""
    return get_customer_value(
        limit=limit,
        customer_id=customer_id
    )


def product_performance_tool(limit=None, stock_code=None):
    """获取商品表现数据，可查询Top N或指定商品。"""
    return get_product_performance(
        limit=limit,
        stock_code=stock_code
    )


def product_comparison_tool(stock_code_a, stock_code_b):
    """比较两个指定商品的销售表现。"""
    return get_product_comparison(
        stock_code_a=stock_code_a,
        stock_code_b=stock_code_b
    )


def product_concentration_tool():
    """获取Top 10商品收入集中度。"""
    return get_product_concentration()


def customer_segments_tool(segment=None):
    """获取客户分群汇总，可按分群名称筛选。"""
    return get_customer_segments(segment=segment)


def segment_comparison_tool(segment_a, segment_b):
    """比较两个指定客户分群的业务表现。"""
    return get_segment_comparison(
        segment_a=segment_a,
        segment_b=segment_b
    )