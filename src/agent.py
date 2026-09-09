import json
import re

from src.grounding_validator import GroundingValidator
from src.llm.siliconflow_provider import SiliconFlowProvider
from src.tool_registry import get_function_schemas
from src.tool_router import run_tool


SYSTEM_PROMPT = (
    "你是一个AI Ecommerce Analyst，负责理解用户的电商业务问题，并基于工具提供的数据进行分析回答。"

    "所有确定性业务事实必须来自当前工具返回结果。"
    "不得猜测、修改或补充工具未提供的数据、单位、币种、时间范围或业务定义。"
    "如果工具返回数值但未提供单位信息，应直接使用该数值。"

    "调用工具时，只使用用户提供或上下文中明确可确定的参数。"
    "如果必要参数无法唯一确定，应向用户澄清，而不是自行生成。"
    "如果工具返回空结果，只说明未找到匹配数据，不要推断额外原因。"

    "所有趋势、排名、比较和业务结论必须有工具数据或明确业务规则支持。"
    "如果证据不足，应明确说明限制，不要将推测表达为事实。"

    "对于比较类问题，优先使用工具返回的comparison、higher_xxx、lower_xxx、winner等字段。"
    "不要自行基于原始字段计算新的比例、倍数、排名或比较结论，除非用户明确要求计算。"
    "当多个指标结果不一致时，应分别说明各指标表现；如果没有用户提供评价标准，不要自行定义唯一整体胜者。"

    "保持回答简洁准确，区分事实、解释和建议。"
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

    def _parse_arguments(self, tool_call):
        """解析单个Tool Call参数。"""
        try:
            return json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return {}

    def _parse_tool_calls(self, tool_calls):
        """解析LLM返回的Tool Calls。"""
        return [
            {
                "name": tool_call.function.name,
                "arguments": self._parse_arguments(tool_call)
            }
            for tool_call in tool_calls or []
        ]

    def _build_tool_signature(self, name, arguments):
        """生成Tool名称和参数的稳定签名，用于识别重复调用。"""
        normalized_arguments = json.dumps(
            arguments,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":")
        )

        return name, normalized_arguments

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
            return "请提供具体年份，例如“2011年11月”或“2011-11”。"

        return None

    def plan(self, question):
        """只执行第一轮LLM调用，用于检查Tool选择和参数提取。"""
        question = self._validate_question(question)

        clarification = self._get_clarification(question)

        if clarification:
            return {
                "question": question,
                "tool_calls": [],
                "content": clarification
            }

        messages = self._build_messages(question)

        response = self.provider.chat(
            messages=messages,
            tools=self.tools
        )

        message = response.choices[0].message

        return {
            "question": question,
            "tool_calls": self._parse_tool_calls(message.tool_calls),
            "content": message.content
        }

    def ask(self, question):
        """返回最终自然语言回答。"""
        result = self.ask_with_trace(question)
        return result["answer"]

    def ask_with_trace(self, question):
        """返回最终回答和Agent完整执行轨迹。"""
        question = self._validate_question(question)

        clarification = self._get_clarification(question)

        if clarification:
            return {
                "question": question,
                "tool_calls": [],
                "tool_results": [],
                "answer": clarification,
                "grounding": None
            }

        messages = self._build_messages(question)

        trace = {
            "question": question,
            "tool_calls": [],
            "tool_results": []
        }

        successful_tool_cache = {}

        for _ in range(self.max_tool_rounds):
            response = self.provider.chat(
                messages=messages,
                tools=self.tools
            )

            message = response.choices[0].message

            if not message.tool_calls:
                answer = message.content

                trace["answer"] = answer
                trace["grounding"] = self.validator.validate(
                    answer,
                    trace["tool_results"],
                    trace["tool_calls"]
                )

                return trace

            assistant_tool_calls = []
            parsed_calls = []

            for tool_call in message.tool_calls:
                arguments = self._parse_arguments(tool_call)

                parsed_calls.append(
                    (
                        tool_call,
                        arguments
                    )
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
                tool_name = tool_call.function.name

                signature = self._build_tool_signature(
                    tool_name,
                    arguments
                )

                if signature in successful_tool_cache:
                    tool_result = successful_tool_cache[signature]
                else:
                    tool_result = run_tool(
                        tool_name,
                        arguments
                    )

                    trace["tool_calls"].append(
                        {
                            "name": tool_name,
                            "arguments": arguments
                        }
                    )

                    trace["tool_results"].append(
                        {
                            "name": tool_name,
                            "result": tool_result
                        }
                    )

                    if tool_result.get("success") is True:
                        successful_tool_cache[signature] = tool_result

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