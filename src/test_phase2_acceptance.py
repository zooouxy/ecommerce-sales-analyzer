import json
import sys
from collections import Counter

from src.agent import EcommerceAgent


sys.stdout.reconfigure(encoding="utf-8")


PHASE_NAME = "Phase 2 — LLM 智能体集成与基于事实的工具调度"

agent = EcommerceAgent()


def normalize_tool_calls(tool_calls):
    """标准化Tool Calls，用于忽略调用顺序但保留重复次数。"""
    return Counter(
        (
            tool_call["name"],
            json.dumps(
                tool_call["arguments"],
                ensure_ascii=False,
                sort_keys=True
            )
        )
        for tool_call in tool_calls
    )


def assert_tool_calls(question, expected_tool_calls):
    """验证首轮Tool选择和参数提取。"""
    plan = agent.plan(question)

    assert (
        plan["tool_calls"]
        == expected_tool_calls
    ), (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_tool_calls}"
        f"\nActual: {plan['tool_calls']}"
    )


def assert_empty_result(
    question,
    expected_tool,
    expected_arguments
):
    """验证空结果完整Agent链路。"""
    trace = agent.ask_with_trace(question)

    expected_tool_calls = [
        {
            "name": expected_tool,
            "arguments": expected_arguments
        }
    ]

    assert (
        trace["tool_calls"]
        == expected_tool_calls
    ), (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_tool_calls}"
        f"\nActual: {trace['tool_calls']}"
    )

    assert len(trace["tool_results"]) == 1

    result = trace["tool_results"][0]["result"]

    assert result["success"] is True
    assert result["tool"] == expected_tool
    assert result["data"] == []

    assert trace["grounding"]["passed"] is True


def assert_multi_tool(
    question,
    expected_tool_calls
):
    """验证Multi-tool选择、参数、执行和重复调用。"""
    trace = agent.ask_with_trace(question)

    actual_calls = normalize_tool_calls(
        trace["tool_calls"]
    )

    expected_calls = normalize_tool_calls(
        expected_tool_calls
    )

    assert actual_calls == expected_calls, (
        f"\nQuestion: {question}"
        f"\nExpected: {expected_tool_calls}"
        f"\nActual: {trace['tool_calls']}"
    )

    assert (
        len(trace["tool_calls"])
        == len(expected_tool_calls)
    ), (
        f"\nUnexpected duplicate or extra Tool Call."
        f"\nQuestion: {question}"
        f"\nActual: {trace['tool_calls']}"
    )

    assert (
        len(trace["tool_results"])
        == len(expected_tool_calls)
    )

    assert all(
        item["result"]["success"]
        for item in trace["tool_results"]
    )


print("\n============================================")
print(PHASE_NAME)
print("Acceptance Test")
print("============================================")


print("\n[1] Core Intent Routing")

intent_cases = [
    (
        "2011年11月销售情况怎么样？",
        [
            {
                "name": "monthly_sales",
                "arguments": {
                    "month": "2011-11"
                }
            }
        ]
    ),
    (
        "客户14646的价值表现怎么样？",
        [
            {
                "name": "customer_value",
                "arguments": {
                    "customer_id": 14646
                }
            }
        ]
    ),
    (
        "商品22423的销售表现怎么样？",
        [
            {
                "name": "product_performance",
                "arguments": {
                    "stock_code": "22423"
                }
            }
        ]
    ),
    (
        "Top 10商品贡献了多少收入？",
        [
            {
                "name": "product_concentration",
                "arguments": {}
            }
        ]
    ),
    (
        "Champions客户群表现怎么样？",
        [
            {
                "name": "customer_segments",
                "arguments": {
                    "segment": "Champions"
                }
            }
        ]
    ),
    (
        "公司整体销售情况怎么样？",
        [
            {
                "name": "sales_kpi",
                "arguments": {}
            }
        ]
    )
]

for question, expected_tool_calls in intent_cases:
    assert_tool_calls(
        question,
        expected_tool_calls
    )

print("PASS")


print("\n[2] Deterministic Monthly Edge Cases")

monthly_cases = [
    (
        "2012年1月的销售情况怎么样？",
        [
            {
                "name": "monthly_sales",
                "arguments": {
                    "month": "2012-01"
                }
            }
        ]
    ),
    (
        "帮我查一下2011/11的销售数据。",
        [
            {
                "name": "monthly_sales",
                "arguments": {
                    "month": "2011-11"
                }
            }
        ]
    ),
    (
        "帮我查一下月度销售。",
        [
            {
                "name": "monthly_sales",
                "arguments": {}
            }
        ]
    )
]

for question, expected_tool_calls in monthly_cases:
    assert_tool_calls(
        question,
        expected_tool_calls
    )

clarification_plan = agent.plan(
    "11月份销售情况怎么样？"
)

assert clarification_plan["tool_calls"] == []
assert clarification_plan["content"]
assert "年份" in clarification_plan["content"]

print("PASS")


print("\n[3] Empty Result Handling")

assert_empty_result(
    "客户999999的价值表现怎么样？",
    "customer_value",
    {
        "customer_id": 999999
    }
)

assert_empty_result(
    "商品ZZZ999的销售表现怎么样？",
    "product_performance",
    {
        "stock_code": "ZZZ999"
    }
)

print("PASS")


print("\n[4] Multi-tool Orchestration")

multi_tool_cases = [
    (
        "整体销售收入是多少，同时Top 10商品占整体商品收入多少？",
        [
            {
                "name": "sales_kpi",
                "arguments": {}
            },
            {
                "name": "product_concentration",
                "arguments": {}
            }
        ]
    ),
    (
        "Champions客户贡献了多少收入，同时整体销售收入是多少？",
        [
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
    ),
    (
        "2011年11月销售收入是多少，同时商品22423的销售表现怎么样？",
        [
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
    )
]

for question, expected_tool_calls in multi_tool_cases:
    assert_multi_tool(
        question,
        expected_tool_calls
    )

print("PASS")


print("\n============================================")
print(f"{PHASE_NAME}: PASS")
print("============================================")