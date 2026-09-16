import json
import re

from src.grounding_validator import GroundingValidator
from src.structured_fallback_renderer import StructuredFallbackRenderer
from src.llm.siliconflow_provider import SiliconFlowProvider
from src.tool_registry import get_function_schemas
from src.tool_router import run_tool


SYSTEM_PROMPT = (
    "你是一个AI Ecommerce Analyst，负责理解用户的电商业务问题，并基于工具提供的证据进行分析回答。"

    "所有当前数据、指标、排名、趋势、比较结果等确定性业务事实必须来自Structured Tool返回结果。"
    "业务定义、解释框架、运营策略和一般业务建议等非结构化知识必须先通过business_knowledge_search检索，"
    "不要仅凭模型自身知识补充为事实。"
    "如果用户的问题同时包含当前数据事实和业务解释或建议，应同时使用对应Structured Tool和business_knowledge_search，"
    "并分别基于两类工具证据回答。"

    "不得猜测、修改或补充工具未提供的数据、单位、币种、时间范围、业务定义或因果关系。"
    "如果工具返回数值但未提供单位信息，应直接使用该数值。"

    "调用工具时，只使用用户提供或上下文中明确可确定的参数。"
    "如果必要参数无法唯一确定，应向用户澄清，而不是自行生成。"
    "如果工具返回空结果，只说明未找到匹配数据，不要推断额外原因。"

    "所有趋势、排名、比较和业务结论必须有工具数据或明确业务规则支持。"
    "所有解释和建议应优先基于检索到的业务知识。"
    "当知识库已经足够回答时，只使用检索到的业务知识，不额外扩写通用做法。"
    "只有当用户明确要求更多建议、更多方案、扩展思路或类似开放式建议时，"
    "才可以补充模型通用电商知识，并必须明确标注为“通用建议”，说明其不来自当前知识库。"
    "通用建议不得改写、覆盖或伪装成Structured Tool事实或RAG知识库内容。"
    "如果证据不足，应明确说明限制，不要将推测表达为事实。"

    "对于比较类问题，优先使用工具返回的comparison、higher_xxx、lower_xxx、winner等字段。"
    "不要自行基于原始字段计算新的比例、倍数、排名或比较结论，除非用户明确要求计算。"
    "当多个指标结果不一致时，应分别说明各指标表现；如果没有用户提供评价标准，不要自行定义唯一整体胜者。"

    "回答时区分事实、解释和建议；结构化数据事实与RAG检索知识不得相互替代。"
    "保持回答简洁准确。"
)


class EcommerceAgent:
    """AI Ecommerce Analyst Agent。"""

    def __init__(self, provider=None, max_tool_rounds=5, validator=None):
        self.provider = provider or SiliconFlowProvider()
        self.tools = get_function_schemas()
        self.max_tool_rounds = max_tool_rounds
        self.validator = validator or GroundingValidator()
        self.structured_fallback_renderer = StructuredFallbackRenderer()

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

    def _requests_general_suggestions(self, question):
        """判断用户是否明确要求知识库之外的通用建议。"""
        patterns = [
            r"除了.*知识库.*(?:建议|策略|方案)",
            r"通用.*(?:建议|策略|方案)",
            r"(?:更多|其他|其它|额外|补充).*(?:建议|策略|方案|思路)",
            r"(?:扩展|拓展).*(?:建议|策略|方案|思路)"
        ]

        return any(
            re.search(pattern, question, flags=re.IGNORECASE)
            for pattern in patterns
        )

    def _get_deterministic_rag_answer(self, question, trace):
        """纯RAG且已有稳定渲染知识时，直接返回确定性知识答案。"""
        if self._requests_general_suggestions(question):
            return None

        if not trace["tool_calls"]:
            return None

        if any(
            item["name"] != "business_knowledge_search"
            for item in trace["tool_calls"]
        ):
            return None

        rendered_texts = []

        for item in trace["tool_results"]:
            if item["name"] != "business_knowledge_search":
                continue

            result = item.get("result", {})

            if result.get("success") is not True:
                return None

            data = result.get("data", result)

            for knowledge_item in data.get("rendered_knowledge", []):
                text = knowledge_item.get("text")

                if text and text not in rendered_texts:
                    rendered_texts.append(text)

        if not rendered_texts:
            return None

        return "\n\n".join(rendered_texts)

    def _render_customer_segment_facts(self, tool_result):
        """将customer_segments结果稳定渲染为结构化事实文本。"""
        if not isinstance(tool_result, dict):
            return ""

        if tool_result.get("success") is not True:
            return ""

        data = tool_result.get("data", [])

        if isinstance(data, dict):
            records = [data]
        elif isinstance(data, list):
            records = data
        else:
            return ""

        rendered = []

        for record in records:
            if not isinstance(record, dict):
                continue

            segment = record.get("segment")

            if not segment:
                continue

            lines = [
                f"**{segment}**",
                f"- 客户数量：{record.get('customer_count')}",
                f"- 总收入贡献：{record.get('total_revenue')}",
                f"- 收入占比：{record.get('revenue_percentage')}%",
                f"- 平均每位客户收入：{record.get('average_revenue_per_customer')}"
            ]

            rendered.append("\n".join(lines))

        return "\n\n".join(rendered)

    def _get_structured_fallback_answer(self, trace):
        """结构化LLM回答不可用时，使用通用确定性Renderer兜底。"""
        tool_calls = trace.get("tool_calls", [])
        tool_results = trace.get("tool_results", [])

        if len(tool_calls) != 1 or len(tool_results) != 1:
            return None

        tool_name = tool_calls[0].get("name")

        if not tool_name or tool_name == "business_knowledge_search":
            return None

        item = tool_results[0]

        if item.get("name") != tool_name:
            return None

        return self.structured_fallback_renderer.render(
            tool_name=tool_name,
            tool_result=item.get("result", {})
        )

    def _get_deterministic_hybrid_answer(self, question, trace):
        """客户分群事实 + RAG知识并存时，确定性组合两类证据。"""
        if self._requests_general_suggestions(question):
            return None

        tool_names = {
            item["name"]
            for item in trace["tool_calls"]
        }

        if not {
            "customer_segments",
            "business_knowledge_search"
        }.issubset(tool_names):
            return None

        structured_texts = []
        knowledge_texts = []

        for item in trace["tool_results"]:
            name = item.get("name")
            result = item.get("result", {})

            if name == "customer_segments":
                text = self._render_customer_segment_facts(result)

                if text:
                    structured_texts.append(text)

            if name == "business_knowledge_search":
                if result.get("success") is not True:
                    continue

                data = result.get("data", result)

                for knowledge_item in data.get("rendered_knowledge", []):
                    text = knowledge_item.get("text")

                    if text and text not in knowledge_texts:
                        knowledge_texts.append(text)

        if not structured_texts or not knowledge_texts:
            return None

        return (
            "**结构化数据**\n\n"
            + "\n\n".join(structured_texts)
            + "\n\n**知识库建议**\n\n"
            + "\n\n".join(knowledge_texts)
        )

    def _normalize_general_suggestions_answer(self, question, answer):
        """为模型通用建议强制统一来源标签，并移除知识库归因语句。"""
        if not self._requests_general_suggestions(question):
            return answer

        if not isinstance(answer, str):
            return answer

        kept_lines = []

        attribution_patterns = [
            r"知识库检索结果",
            r"基于知识库",
            r"来自知识库",
            r"知识库中.*(?:建议|策略|框架)",
            r"根据知识库"
        ]

        for line in answer.splitlines():
            stripped = line.strip()

            if stripped and any(
                re.search(
                    pattern,
                    stripped,
                    flags=re.IGNORECASE
                )
                for pattern in attribution_patterns
            ):
                continue

            kept_lines.append(line)

        body = "\n".join(kept_lines)

        body = re.sub(
            r"\n{3,}",
            "\n\n",
            body
        ).strip()

        header = (
            "**通用建议（非知识库内容）**\n\n"
            "以下建议来自模型通用电商知识，"
            "不属于当前知识库检索内容。"
        )

        if not body:
            return header

        return header + "\n\n" + body

    def _line_contains_unsupported_number(self, line, values):
        """判断文本行是否包含Grounding标记的无依据数字。"""
        if not isinstance(line, str):
            return False

        for value in values:
            value = str(value)

            if re.search(
                rf"(?<![\d.]){re.escape(value)}(?![\d.])",
                line
            ):
                return True

        return False

    def _line_contains_unsupported_currency(self, line):
        """判断文本行是否包含证据未支持的币种或货币单位。"""
        currency_terms = (
            "人民币",
            "RMB",
            "CNY",
            "美元",
            "USD",
            "欧元",
            "EUR",
            "英镑",
            "GBP",
            "元"
        )

        return any(
            term in line
            for term in currency_terms
        )

    def _sanitize_grounding_answer(self, answer, grounding):
        """确定性删除包含无依据数字或币种的内容行。"""
        if not isinstance(answer, str):
            return answer

        warnings = grounding.get("warnings", [])

        unsupported_numbers = set()
        remove_currency_lines = False

        for warning in warnings:
            if not isinstance(warning, dict):
                continue

            warning_type = warning.get("type")

            if warning_type == "unsupported_numbers":
                unsupported_numbers.update(
                    str(value)
                    for value in warning.get("values", [])
                )

            if warning_type == "unsupported_currency":
                remove_currency_lines = True

        if not unsupported_numbers and not remove_currency_lines:
            return answer

        kept_lines = []

        for line in answer.splitlines():
            if (
                unsupported_numbers
                and self._line_contains_unsupported_number(
                    line,
                    unsupported_numbers
                )
            ):
                continue

            if (
                remove_currency_lines
                and self._line_contains_unsupported_currency(line)
            ):
                continue

            kept_lines.append(line)

        sanitized = "\n".join(kept_lines)

        sanitized = re.sub(
            r"\n{3,}",
            "\n\n",
            sanitized
        )

        return sanitized.strip()

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
        allow_general_knowledge = self._requests_general_suggestions(
            question
        )

        for _ in range(self.max_tool_rounds):
            response = self.provider.chat(
                messages=messages,
                tools=self.tools
            )

            message = response.choices[0].message

            if not message.tool_calls:
                answer = message.content

                if not isinstance(answer, str) or not answer.strip():
                    fallback_answer = self._get_structured_fallback_answer(
                        trace
                    )

                    if fallback_answer is not None:
                        answer = fallback_answer
                        trace["answer_mode"] = (
                            "deterministic_structured_fallback"
                        )

                grounding = self.validator.validate(
                    answer,
                    trace["tool_results"],
                    trace["tool_calls"],
                    allow_general_knowledge=allow_general_knowledge
                )

                sanitized_answer = self._sanitize_grounding_answer(
                    answer,
                    grounding
                )

                if sanitized_answer != answer:
                    answer = sanitized_answer
                    grounding = self.validator.validate(
                        answer,
                        trace["tool_results"],
                        trace["tool_calls"],
                        allow_general_knowledge=allow_general_knowledge
                    )
                    trace["grounding_sanitizer_applied"] = True

                normalized_answer = self._normalize_general_suggestions_answer(
                    question,
                    answer
                )

                if normalized_answer != answer:
                    answer = normalized_answer
                    grounding = self.validator.validate(
                        answer,
                        trace["tool_results"],
                        trace["tool_calls"],
                        allow_general_knowledge=allow_general_knowledge
                    )
                    trace["provenance_normalization_applied"] = True

                # 后处理可能把原本非空的LLM回答整段删除。
                # 最终返回前再次检查，并仅使用已支持的结构化Tool结果兜底。
                if not isinstance(answer, str) or not answer.strip():
                    fallback_answer = self._get_structured_fallback_answer(
                        trace
                    )

                    if fallback_answer is not None:
                        answer = fallback_answer
                        trace["answer_mode"] = (
                            "deterministic_structured_fallback"
                        )
                        grounding = self.validator.validate(
                            answer,
                            trace["tool_results"],
                            trace["tool_calls"],
                            allow_general_knowledge=allow_general_knowledge
                        )

                trace["answer"] = answer
                trace["grounding"] = grounding

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

            deterministic_hybrid_answer = self._get_deterministic_hybrid_answer(
                question,
                trace
            )

            if deterministic_hybrid_answer is not None:
                trace["answer"] = deterministic_hybrid_answer
                trace["grounding"] = self.validator.validate(
                    deterministic_hybrid_answer,
                    trace["tool_results"],
                    trace["tool_calls"],
                    allow_general_knowledge=allow_general_knowledge
                )
                trace["answer_mode"] = "deterministic_hybrid"

                return trace

            deterministic_rag_answer = self._get_deterministic_rag_answer(
                question,
                trace
            )

            if deterministic_rag_answer is not None:
                trace["answer"] = deterministic_rag_answer
                trace["grounding"] = self.validator.validate(
                    deterministic_rag_answer,
                    trace["tool_results"],
                    trace["tool_calls"],
                    allow_general_knowledge=allow_general_knowledge
                )
                trace["answer_mode"] = "deterministic_rag"

                return trace

        raise RuntimeError(
            "Agent exceeded maximum tool call rounds"
        )