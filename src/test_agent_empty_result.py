import sys

from src.agent import EcommerceAgent


sys.stdout.reconfigure(encoding="utf-8")


agent = EcommerceAgent()

question = "客户999999的价值表现怎么样？"

print("\n--- Missing Customer ---")
print("Question:", question)

trace = agent.ask_with_trace(question)

print("Tool Calls:", trace["tool_calls"])
print("Tool Results:", trace["tool_results"])
print("Answer:", trace["answer"])
print("Grounding:", trace["grounding"])


assert trace["tool_calls"] == [
    {
        "name": "customer_value",
        "arguments": {
            "customer_id": 999999
        }
    }
]

assert len(trace["tool_results"]) == 1

tool_result = trace["tool_results"][0]["result"]

assert tool_result["success"] is True
assert tool_result["tool"] == "customer_value"
assert tool_result["data"] == []

print(
    "\nMissing Customer Empty Result: PASS"
)