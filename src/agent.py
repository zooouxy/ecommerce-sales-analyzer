import json
import re

from src.grounding_validator import GroundingValidator
from src.llm.siliconflow_provider import SiliconFlowProvider
from src.tool_registry import get_function_schemas
from src.tool_router import run_tool


SYSTEM_PROMPT = (
    "你是一个AI Ecommerce Analyst。"
    "你的职责是理解用户的电商业务问题，并在需要业务数据时调用工具。"

    "所有确定性业务事实必须来自本次工具返回结果。"
    "不得自行猜测、修改或补充工具未提供的数据、单位或业务事实。"
    "如果工具没有明确提供币种，不要为金额添加元、人民币、美元等货币单位。"

    "不得为用户没有提供、且无法从当前上下文唯一确定的工具参数自行生成值。"
    "如果参数是可选的，可以直接省略该参数。"
    "如果缺少的信息导致无法唯一确定必要参数，应先向用户澄清，而不是猜测。"

    "当工具执行成功但返回空数据时，只说明当前查询没有找到匹配记录。"
    "除非工具结果明确提供原因，否则不要推断空结果产生的原因。"

    "比较、排名、趋势和业务分类结论必须有相应的数据或业务规则支持。"
    "如果当前证据不足，应明确说明证据不足，不要把推测表述成事实。"

    "只调用回答当前问题所必需的工具。"
    "如果一个问题确实需要多个工具才能回答，可以继续调用工具。"
    "如果同一个工具使用相同参数已经成功返回结果，不要重复调用。"
    "只有在需要不同参数或新的数据时，才再次调用同一个工具。"

    "可以在用户明确需要时，基于工具结果进行简单、直接且逻辑成立的数学推导。"
    "不要主动计算或补充用户没有询问的额外指标。"

    "请区分事实、解释和建议，"
    "并根据工具结果用简洁、准确的中文回答用户问题。"
)

class EcommerceAgent:
    """AI Ecommerce Analyst Agent。"""

    def __init__(self, provider=None, max_tool_rounds=5, validator=None):
        self.provider = provider or SiliconFlowProvider()
        self.tools = get_function_schemas()
        self.max_tool_rounds = max_tool_rounds
        self.validator = validator or GroundingValidator()

    def _validate_question(self, question):
        """校验并标准化用户问题。"""
        if not isinstance(question, str):
            raise TypeError("question must be a string")

        question = question.strip()

        if not question:
            raise ValueError("question cannot be empty")

        return question

    def _build_messages(self, question):
        """构建初始对话消息。"""
        return [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ]

    def _parse_tool_calls(self, tool_calls):
        """解析LLM返回的Tool Calls。"""
        parsed_calls = []

        for tool_call in tool_calls or []:
            try:
                arguments = json.loads(
                    tool_call.function.arguments
                )
            except json.JSONDecodeError:
                arguments = {}

            parsed_calls.append(
                {
                    "name": tool_call.function.name,
                    "arguments": arguments
                }
            )

        return parsed_calls

    def _get_clarification(self, question):
        """检查月份参数是否缺少年份。"""
        has_year_month = bool(
            re.search(
                r"\b\d{4}\s*[年/-]\s*\d{1,2}\s*月?",
                question
            )
        )

        has_month_only = bool(
            re.search(
                r"(?<!\d)(1[0-2]|[1-9])月份?",
                question
            )
        )

        if has_month_only and not has_year_month:
            return (
                "请提供具体年份，例如“2011年11月”或“2011-11”。"
            )

        return None

    def plan(self, question):
        """只执行第一轮LLM调用，用于检查Tool选择和参数提取。"""
        question = self._validate_question(question)

        clarification = self._get_clarification(
            question
        )

        if clarification:
            return {
                "question": question,
                "tool_calls": [],
                "content": clarification
            }

        messages = self._build_messages(
            question
        )

        response = self.provider.chat(
            messages=messages,
            tools=self.tools
        )

        message = response.choices[0].message

        return {
            "question": question,
            "tool_calls": self._parse_tool_calls(
                message.tool_calls
            ),
            "content": message.content
        }

    def ask(self, question):
        """返回最终自然语言回答。"""
        result = self.ask_with_trace(
            question
        )

        return result["answer"]

    def ask_with_trace(self, question):
        """返回最终回答和Agent完整执行轨迹。"""
        question = self._validate_question(
            question
        )

        clarification = self._get_clarification(
            question
        )

        if clarification:
            return {
                "question": question,
                "tool_calls": [],
                "tool_results": [],
                "answer": clarification,
                "grounding": None
            }

        messages = self._build_messages(
            question
        )

        trace = {
            "question": question,
            "tool_calls": [],
            "tool_results": []
        }

        for _ in range(
            self.max_tool_rounds
        ):
            response = self.provider.chat(
                messages=messages,
                tools=self.tools
            )

            message = response.choices[0].message

            if not message.tool_calls:
                answer = message.content

                trace["answer"] = answer
                trace["grounding"] = (
                    self.validator.validate(
                        answer,
                        trace["tool_results"],
                        trace["tool_calls"]
                    )
                )

                return trace

            assistant_tool_calls = []
            parsed_calls = []

            for tool_call in message.tool_calls:
                try:
                    arguments = json.loads(
                        tool_call.function.arguments
                    )
                except json.JSONDecodeError:
                    arguments = {}

                parsed_calls.append(
                    (
                        tool_call,
                        arguments
                    )
                )

                trace["tool_calls"].append(
                    {
                        "name": tool_call.function.name,
                        "arguments": arguments
                    }
                )

                assistant_tool_calls.append(
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                )

            messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": assistant_tool_calls
                }
            )

            for tool_call, arguments in parsed_calls:
                tool_result = run_tool(
                    tool_call.function.name,
                    arguments
                )

                trace["tool_results"].append(
                    {
                        "name": tool_call.function.name,
                        "result": tool_result
                    }
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

        raise RuntimeError(
            "Agent exceeded maximum tool call rounds"
        )