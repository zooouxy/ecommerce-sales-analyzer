from src.tools import (
    customer_segments_tool,
    customer_value_tool,
    monthly_sales_tool,
    product_concentration_tool,
    product_performance_tool,
    sales_kpi_tool
)


TOOL_REGISTRY = {
    "sales_kpi": {
        "function": sales_kpi_tool,
        "description": (
            "查询整体销售核心指标，包括总收入、总订单数、"
            "总商品数量和平均订单价值。"
            "适用于整体销售概况，不用于查询指定月份。"
        ),
        "parameters": {}
    },

    "monthly_sales": {
        "function": monthly_sales_tool,
        "description": (
            "查询月度销售数据，包括月份、销售收入、订单数和收入环比增长率。"
            "month参数为可选参数。"
            "如果用户明确指定了完整月份，则传入YYYY-MM格式的month。"
            "如果用户没有指定具体月份，可以省略month并查询全部月度数据。"
            "如果用户只提供月份但缺少年份，不要猜测年份，应先要求用户澄清。"
        ),
        "parameters": {
            "month": {
                "type": "string",
                "required": False,
                "description": (
                    "可选月份，格式YYYY-MM，例如2011-11。"
                    "用户没有指定具体月份时应省略此参数；"
                    "不得自行补充用户没有提供的年份或月份。"
                )
            }
        }
    },

    "customer_value": {
        "function": customer_value_tool,
        "description": (
            "查询客户价值数据，包括订单数、总收入、平均订单价值、"
            "首次购买时间和最近购买时间。"
            "可查询指定客户，也可查询客户价值列表。"
        ),
        "parameters": {
            "limit": {
                "type": "integer",
                "required": False,
                "description": "可选返回记录数量，必须为正整数。"
            },
            "customer_id": {
                "type": "integer",
                "required": False,
                "description": "可选客户ID，必须为正整数。"
            }
        }
    },

    "product_performance": {
        "function": product_performance_tool,
        "description": (
            "查询商品销售表现，包括StockCode、商品描述、收入、销量和订单数。"
            "适用于查询指定商品或商品表现列表。"
        ),
        "parameters": {
            "limit": {
                "type": "integer",
                "required": False,
                "description": "可选返回记录数量，必须为正整数。"
            },
            "stock_code": {
                "type": "string",
                "required": False,
                "description": "可选商品StockCode，例如22423。"
            }
        }
    },

    "product_concentration": {
        "function": product_concentration_tool,
        "description": (
            "查询商品收入集中度，包括全部商品收入、Top 10商品收入"
            "以及Top 10商品收入占整体商品收入的比例。"
            "适用于判断收入是否集中在少数商品。"
        ),
        "parameters": {}
    },

    "customer_segments": {
        "function": customer_segments_tool,
        "description": (
            "查询客户分群表现。可返回指定客户分群的客户数量、总收入、"
            "占整体收入的比例以及平均每位客户收入。"
            "当用户询问某个客户分群的收入占比、客户数量、总收入"
            "或平均收入时，优先使用此工具，无需额外查询整体销售KPI。"
        ),
        "parameters": {
            "segment": {
                "type": "string",
                "required": False,
                "description": (
                    "可选客户分群名称，可使用：Champions、Loyal Customers、"
                    "Regular Customers、High Value Lost、Lost Customers、"
                    "At Risk、Big Spenders。"
                )
            }
        }
    }
}


def get_tool(name):
    """根据名称获取Tool配置。"""
    if name not in TOOL_REGISTRY:
        raise ValueError(
            f"unknown tool: {name}"
        )

    return TOOL_REGISTRY[name]


def execute_tool(name, **kwargs):
    """执行指定Tool。"""
    tool = get_tool(name)
    return tool["function"](**kwargs)


def build_function_schema(name):
    """生成内部统一Function Schema。"""
    tool = get_tool(name)

    properties = {}
    required = []

    for param_name, param_config in tool["parameters"].items():
        properties[param_name] = {
            "type": param_config["type"],
            "description": param_config["description"]
        }

        if param_config.get("required"):
            required.append(param_name)

    return {
        "type": "function",
        "name": name,
        "description": tool["description"],
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False
        },
        "strict": True
    }


def get_function_schemas():
    """返回全部Function Schema。"""
    return [
        build_function_schema(name)
        for name in TOOL_REGISTRY
    ]