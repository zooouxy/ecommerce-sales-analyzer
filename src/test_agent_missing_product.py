import sys

from src.agent import EcommerceAgent


sys.stdout.reconfigure(encoding="utf-8")


agent = EcommerceAgent()

question = "商品ZZZ999的销售表现怎么样？"

print("\n--- Missing Product ---")
print("Question:", question)

trace = agent.ask_with_trace(question)

print("Tool Calls:", trace["tool_calls"])
print("Tool Results:", trace["tool_results"])
print("Answer:", trace["answer"])
print("Grounding:", trace["grounding"])


assert trace["tool_calls"] == [
    {
        "name": "product_performance",
        "arguments": {
            "stock_code": "ZZZ999"
        }
    }
]

assert len(trace["tool_results"]) == 1

tool_result = trace["tool_results"][0]["result"]

assert tool_result["success"] is True
assert tool_result["tool"] == "product_performance"
assert tool_result["data"] == []

print(
    "\nMissing Product Empty Result: PASS"
)