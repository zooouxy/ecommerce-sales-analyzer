import os

from dotenv import load_dotenv
from openai import OpenAI

from src.llm.base import LLMProvider


load_dotenv()


class SiliconFlowProvider(LLMProvider):
    """SiliconFlow LLM Provider。"""

    def __init__(self, model=None):
        api_key = os.getenv("SILICONFLOW_API_KEY")
        model = model or os.getenv("SILICONFLOW_MODEL")

        if not api_key:
            raise ValueError(
                "SILICONFLOW_API_KEY is not configured"
            )

        if not model:
            raise ValueError(
                "SILICONFLOW_MODEL is not configured"
            )

        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1"
        )

    def _convert_tools(self, tools):
        """将内部Tool Schema转换为OpenAI兼容格式。"""
        if not tools:
            return None

        converted_tools = []

        for tool in tools:
            converted_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"]
                    }
                }
            )

        return converted_tools

    def chat(self, messages, tools=None):
        """调用SiliconFlow Chat Completions API。"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        converted_tools = self._convert_tools(tools)

        if converted_tools:
            kwargs["tools"] = converted_tools

        return self.client.chat.completions.create(
            **kwargs
        )