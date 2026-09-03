import sys

from src.agent import EcommerceAgent


sys.stdout.reconfigure(encoding="utf-8")


agent = EcommerceAgent()


test_cases = [
    {
        "name": "Sales KPI + Product Concentration",
        "question": (
            "整体销售收入是多少，同时Top 10商品占整体商品收入多少？"
        ),
        "expected_tool_calls": [
            {
                "name": "sales_kpi",
                "arguments": {}
            },
            {
                "name": "product_concentration",
                "arguments": {}
            }
        ]
    },
    {
        "name": "Customer Segments + Sales KPI",
        "question": (
            "Champions客户贡献了多少收入，同时整体销售收入是多少？"
        ),
        "expected_tool_calls": [
            {
                "name": "customer_segments",
                "arguments": {
                    "segment": "Champions"
                }
            },
            {
                "name": "sales_kpi",
                "arguments": {}
            }
        ]
    },
    {
        "name": "Monthly Sales + Product Performance",
        "question": (
            "2011年11月销售收入是多少，同时商品22423的销售表现怎么样？"
        ),
        "expected_tool_calls": [
            {
                "name": "monthly_sales",
                "arguments": {
                    "month": "2011-11"
                }
            },
            {
                "name": "product_performance",
                "arguments": {
                    "stock_code": "22423"
                }
            }
        ]
    }
]


for test_case in test_cases:
    print(f"\n--- {test_case['name']} ---")
    print("Question:", test_case["question"])

    trace = agent.ask_with_trace(
        test_case["question"]
    )

    print("Tool Calls:", trace["tool_calls"])
    print("Tool Results:", trace["tool_results"])
    print("Answer:", trace["answer"])
    print("Grounding:", trace["grounding"])

    assert (
        trace["tool_calls"]
        == test_case["expected_tool_calls"]
    )

    assert (
        len(trace["tool_results"])
        == len(test_case["expected_tool_calls"])
    )

    assert all(
        tool_result["result"]["success"]
        for tool_result in trace["tool_results"]
    )

    print("PASS")


print(
    "\nMulti-tool Agent Tests: PASS"
)