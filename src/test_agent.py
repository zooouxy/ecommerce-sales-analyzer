import sys

from src.agent import EcommerceAgent


sys.stdout.reconfigure(encoding="utf-8")


agent = EcommerceAgent()


deterministic_cases = [
    {
        "name": "Explicit Month",
        "question": "2012年1月的销售情况怎么样？",
        "expected_tool_calls": [
            {
                "name": "monthly_sales",
                "arguments": {
                    "month": "2012-01"
                }
            }
        ]
    },
    {
        "name": "Normalized Month Format",
        "question": "帮我查一下2011/11的销售数据。",
        "expected_tool_calls": [
            {
                "name": "monthly_sales",
                "arguments": {
                    "month": "2011-11"
                }
            }
        ]
    },
    {
        "name": "Missing Year Clarification",
        "question": "11月份销售情况怎么样？",
        "expected_tool_calls": []
    },
    {
        "name": "Optional Month Omitted",
        "question": "帮我查一下月度销售。",
        "expected_tool_calls": [
            {
                "name": "monthly_sales",
                "arguments": {}
            }
        ]
    }
]


for test_case in deterministic_cases:
    print(f"\n--- {test_case['name']} ---")
    print("Question:", test_case["question"])

    plan = agent.plan(
        test_case["question"]
    )

    print(
        "Tool Calls:",
        plan["tool_calls"]
    )

    print(
        "Content:",
        plan["content"]
    )

    assert (
        plan["tool_calls"]
        == test_case["expected_tool_calls"]
    )

    if test_case["name"] == "Missing Year Clarification":
        assert plan["content"]
        assert "年份" in plan["content"]

    print("PASS")


print(
    "\nDeterministic Monthly Sales Edge Cases: PASS"
)


print(
    "\n--- Relative Time Observation ---"
)

relative_time_question = "上个月销售怎么样？"

print(
    "Question:",
    relative_time_question
)

relative_time_plan = agent.plan(
    relative_time_question
)

print(
    "Tool Calls:",
    relative_time_plan["tool_calls"]
)

print(
    "Content:",
    relative_time_plan["content"]
)

print(
    "Known Limitation: relative-time interpretation "
    "may vary because the dataset is static historical data."
)