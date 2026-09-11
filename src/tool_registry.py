from src.tools import (
    business_knowledge_search_tool,
    customer_segments_tool,
    customer_value_tool,
    month_comparison_tool,
    monthly_sales_tool,
    monthly_trend_insights_tool,
    product_comparison_tool,
    product_concentration_tool,
    product_performance_tool,
    sales_kpi_tool,
    segment_comparison_tool
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
            "适用于查询指定月份的数据，或获取完整月度时间序列。"
            "month参数为可选参数。"
            "如果用户明确指定了完整月份，则传入YYYY-MM格式的month。"
            "如果用户没有指定具体月份，可以省略month并查询全部月度数据。"
            "如果用户只提供月份但缺少年份，不要猜测年份，应先要求用户澄清。"
            "如果用户询问哪个月收入最高、订单最多、增长最快、下降最明显"
            "或最新月份等关键趋势，应优先使用monthly_trend_insights工具。"
            "如果用户明确要求比较两个月份，应优先使用month_comparison工具。"
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

    "monthly_trend_insights": {
        "function": monthly_trend_insights_tool,
        "description": (
            "查询月度销售关键趋势洞察。"
            "适用于回答哪个月销售收入最高、哪个月订单最多、"
            "哪个月收入增长最快、哪个月收入下降最明显，"
            "以及数据集中最新月份表现等问题。"
            "收入最高、订单最多、最大增长和最大下降均基于完整月份比较。"
            "环比趋势比较要求当前月和前一个月均为完整月份。"
            "最新月份即使是不完整月份仍会返回，并通过is_partial_month标记。"
            "当用户询问月度排名、峰值、低谷或关键趋势时，"
            "优先使用此工具，而不是让模型自行分析完整monthly_sales列表。"
        ),
        "parameters": {}
    },

    "month_comparison": {
        "function": month_comparison_tool,
        "description": (
            "比较两个明确指定月份的销售表现，包括销售收入、订单数、"
            "收入差值、收入差异百分比、订单差值、订单差异百分比，"
            "以及哪个月份收入或订单更高。"
            "适用于用户明确要求比较两个月份、询问两个指定月份差多少"
            "或哪个指定月份表现更好的问题。"
            "month_a是比较基准月份，month_b是被比较月份，"
            "差值和差异百分比均按month_b相对month_a计算。"
            "如果某个月是不完整月份，工具仍会返回数据，"
            "但comparison_is_fully_comparable会为false，"
            "并在partial_months中标记不完整月份。"
            "不得自行生成用户没有提供的月份。"
        ),
        "parameters": {
            "month_a": {
                "type": "string",
                "required": True,
                "description": (
                    "第一个比较月份，也是差异计算的基准月份。"
                    "格式必须为YYYY-MM，例如2011-10。"
                )
            },
            "month_b": {
                "type": "string",
                "required": True,
                "description": (
                    "第二个比较月份，差值按month_b减month_a计算。"
                    "格式必须为YYYY-MM，例如2011-11。"
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
            "查询单个商品或商品列表的销售表现，包括StockCode、"
            "商品描述、收入、销量和订单数。"
            "适用于查询一个指定商品，或查询商品表现列表和Top N。"
            "如果用户同时提供两个明确的StockCode，并询问收入、销量、"
            "订单数、差值、哪个更多或整体销售表现等任何比较问题，"
            "不要使用此工具，应使用product_comparison工具。"
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

    "product_comparison": {
        "function": product_comparison_tool,
        "description": (
            "比较两个明确指定StockCode的商品销售表现。"
            "只要用户同时提供两个商品StockCode并要求比较，"
            "应优先使用此工具。"
            "可比较销售收入、销量和订单数，包括哪个商品收入更高、"
            "哪个商品销量更多、哪个商品订单数更多、两个商品订单差多少、"
            "收入差多少、销量差多少，以及两个商品整体销售表现。"
            "stock_code_a是比较基准商品，stock_code_b是被比较商品，"
            "所有差值和差异百分比均按stock_code_b相对stock_code_a计算。"
            "如果某个StockCode没有匹配记录，工具会通过"
            "missing_stock_codes返回缺失商品。"
            "不得自行生成用户没有提供的StockCode。"
        ),
        "parameters": {
            "stock_code_a": {
                "type": "string",
                "required": True,
                "description": (
                    "用户首先提供的商品StockCode，也是差异计算基准。"
                    "例如22423。"
                )
            },
            "stock_code_b": {
                "type": "string",
                "required": True,
                "description": (
                    "用户随后提供的第二个商品StockCode。"
                    "差值按stock_code_b减stock_code_a计算。"
                    "例如85123A。"
                )
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
            "查询单个客户分群或全部客户分群的业务表现。"
            "可返回客户数量、总收入、整体收入占比以及平均每客户收入。"
            "如果用户同时明确提供两个客户分群并要求比较客户数量、"
            "收入贡献、收入占比、平均每客户收入或整体表现，"
            "不要使用此工具，应使用segment_comparison工具。"
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
    },

    "segment_comparison": {
        "function": segment_comparison_tool,
        "description": (
            "比较两个明确指定客户分群的业务表现。"
            "只要用户同时指定两个分群并要求比较，应优先使用此工具。"
            "可比较客户数量、总收入、整体收入占比和平均每客户收入，"
            "并直接返回差值、差异百分比和各指标更高的分群。"
            "收入占比revenue_percentage之间的差异使用百分点"
            "revenue_percentage_difference_pp表示，不要将其解释为"
            "两个百分比之间的相对增长率。"
            "segment_a是比较基准分群，segment_b是被比较分群，"
            "普通数值差值均按segment_b减segment_a计算。"
            "如果不同指标的胜者不同，应分别说明各指标结果；"
            "没有综合评价标准时，不要自行判断唯一整体胜者。"
        ),
        "parameters": {
            "segment_a": {
                "type": "string",
                "required": True,
                "description": (
                    "用户首先提供的客户分群，也是差异计算基准。"
                    "可使用：Champions、Loyal Customers、Regular Customers、"
                    "High Value Lost、Lost Customers、At Risk、Big Spenders。"
                )
            },
            "segment_b": {
                "type": "string",
                "required": True,
                "description": (
                    "用户随后提供的第二个客户分群。"
                    "普通指标差值按segment_b减segment_a计算。"
                    "可使用：Champions、Loyal Customers、Regular Customers、"
                    "High Value Lost、Lost Customers、At Risk、Big Spenders。"
                )
            }
        }
    },
    "business_knowledge_search": {
        "function": business_knowledge_search_tool,
        "description": (
            "检索电商业务知识库，用于回答业务定义、指标含义、分析解释框架、"
            "客户分群运营策略、商品表现解读、销售趋势解读和一般业务建议。"
            "该工具提供非结构化业务知识，不负责查询当前销售收入、订单数、"
            "销量、客户数量、排名、增长率或其他确定性业务数值。"
            "纯数据事实应使用对应Structured Tool；"
            "如果用户同时询问数据事实和业务解释或建议，"
            "可以同时调用对应Structured Tool和本工具。"
            "query应保留用户问题中需要检索的业务语义，不要自行添加新的业务事实。"
        ),
        "parameters": {
            "query": {
                "type": "string",
                "required": True,
                "description": (
                    "要检索的业务知识问题或语义查询，例如"
                    "Champions客户应该怎么运营？"
                    "或平均订单价值是什么？"
                )
            },
            "top_k": {
                "type": "integer",
                "required": False,
                "description": (
                    "可选返回知识片段数量，必须为正整数；"
                    "未指定时默认返回3条。"
                )
            }
        }
    }
}


def get_tool(name):
    """根据名称获取Tool配置。"""
    if name not in TOOL_REGISTRY:
        raise ValueError(f"unknown tool: {name}")

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