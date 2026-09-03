from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """LLM Provider统一接口。"""

    @abstractmethod
    def chat(self, messages, tools=None):
        """发送消息并返回模型原始响应。"""
        raise NotImplementedError