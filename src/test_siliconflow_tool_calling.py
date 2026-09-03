import json
import sys
from src.llm.siliconflow_provider import SiliconFlowProvider
from src.tool_registry import get_function_schemas
from src.tool_router import run_tool


sys.stdout.reconfigure(encoding="utf-8")

provider = SiliconFlowProvider()

messages = [
    {
        "role": "system",
        "content": (
            "你是一个AI Ecommerce Analyst。"
            "所有确定性业务数据必须来自工具返回结果，"
            "不要自行猜测或修改数据。"
            "请根据工具结果，用简洁、准确的中文回答用户问题。"
        )
    },
    {
        "role": "user",
        "content": "2011年11月的销售收入、订单数和环比增长率是多少？"
    }
]

response = provider.chat(
    messages=messages,
    tools=get_function_schemas()
)

message = response.choices[0].message

if not message.tool_calls:
    print(message.content)
    raise SystemExit

messages.append(
    {
        "role": "assistant",
        "content": message.content,
        "tool_calls": [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            }
            for tool_call in message.tool_calls
        ]
    }
)

for tool_call in message.tool_calls:
    tool_name = tool_call.function.name
    arguments = json.loads(
        tool_call.function.arguments
    )

    tool_result = run_tool(
        tool_name,
        arguments
    )

    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(
                tool_result,
                ensure_ascii=False
            )
        }
    )

final_response = provider.chat(
    messages=messages,
    tools=get_function_schemas()
)

print(final_response.choices[0].message.content)