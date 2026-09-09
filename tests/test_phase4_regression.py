import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.tool_router import run_tool

def check_tool(name, args):
    print("=" * 70)
    print("TOOL:", name)

    result = run_tool(
        name,
        args
    )

    print(result)

    assert result["success"] is True
    assert "data" in result

    print("PASS")


def main():

    tests = [

        (
            "sales_kpi",
            {}
        ),

        (
            "monthly_sales",
            {
                "month": "2011-11"
            }
        ),

        (
            "monthly_trend_insights",
            {}
        ),

        (
            "month_comparison",
            {
                "month_a": "2011-10",
                "month_b": "2011-11"
            }
        ),

        (
            "customer_value",
            {
                "limit": 5
            }
        ),

        (
            "product_performance",
            {
                "limit": 5
            }
        ),

        (
            "product_comparison",
            {
                "stock_code_a": "22423",
                "stock_code_b": "85123A"
            }
        ),

        (
            "product_concentration",
            {}
        ),

        (
            "customer_segments",
            {}
        ),

        (
            "segment_comparison",
            {
                "segment_a": "Champions",
                "segment_b": "Loyal Customers"
            }
        ),
    ]


    for name, args in tests:
        check_tool(
            name,
            args
        )


    print("=" * 70)
    print("ALL PHASE 4 TOOL REGRESSION TESTS PASSED")


if __name__ == "__main__":
    main()