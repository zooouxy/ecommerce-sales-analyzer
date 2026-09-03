from src.llm.siliconflow_provider import (
    SiliconFlowProvider
)


provider = SiliconFlowProvider()

response = provider.chat(
    messages=[
        {
            "role": "user",
            "content": "请只回复：SiliconFlow connection successful"
        }
    ]
)

print(response.choices[0].message.content)