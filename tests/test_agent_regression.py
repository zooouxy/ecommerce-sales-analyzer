import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


from src.agent import EcommerceAgent


def run_case(question, expected_tool):

    print("=" * 70)
    print("QUESTION:")
    print(question)

    trace = agent.ask_with_trace(question)

    print("\nANSWER:")
    print(trace["answer"])

    print("\nTOOL CALLS:")
    print(trace["tool_calls"])

    print("\nGROUNDING:")
    print(trace["grounding"])


    # Tool调用检查
    assert len(trace["tool_calls"]) > 0, (
        f"No tool called for question: {question}"
    )

    actual_tool = trace["tool_calls"][0]["name"]

    assert actual_tool == expected_tool, (
        f"Expected {expected_tool}, got {actual_tool}"
    )


    # Grounding检查
    assert trace["grounding"]["passed"] is True, (
        f"Grounding failed for question: {question}"
    )


    print("PASS")


def main():

    cases = [

        (
            "整体销售情况怎么样？",
            "sales_kpi"
        ),

        (
            "哪个月销售收入最高？",
            "monthly_trend_insights"
        ),

        (
            "2011-10和2011-11哪个月收入更高？",
            "month_comparison"
        ),

        (
            "商品22423和85123A哪个收入更高？",
            "product_comparison"
        ),

        (
            "Champions和Loyal Customers哪个收入贡献更高？",
            "segment_comparison"
        ),

    ]


    for question, expected_tool in cases:
        run_case(
            question,
            expected_tool
        )


    print("=" * 70)
    print(
        "ALL PHASE 4 AGENT REGRESSION TESTS PASSED"
    )


if __name__ == "__main__":

    agent = EcommerceAgent()

    main()