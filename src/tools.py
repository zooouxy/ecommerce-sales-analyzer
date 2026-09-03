from src.query_service import (
    get_sales_kpi,
    get_monthly_sales,
    get_customer_value,
    get_product_performance,
    get_product_concentration,
    get_customer_segments
)


def sales_kpi_tool():
    """获取整体销售KPI。"""
    return get_sales_kpi()


def monthly_sales_tool(month=None):
    """获取月度销售数据，可按YYYY-MM筛选。"""
    return get_monthly_sales(month=month)


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


def product_concentration_tool():
    """获取Top 10商品收入集中度。"""
    return get_product_concentration()


def customer_segments_tool(segment=None):
    """获取客户分群汇总，可按分群名称筛选。"""
    return get_customer_segments(segment=segment)