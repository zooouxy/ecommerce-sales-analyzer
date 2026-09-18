import re


CURRENCY_TERMS = {
    "元",
    "人民币",
    "RMB",
    "CNY",
    "美元",
    "USD",
    "欧元",
    "EUR",
    "英镑",
    "GBP"
}

TEXT_NUMERIC_EVIDENCE_KEYS = {
    "stock_code",
    "month",
    "first_purchase_date",
    "last_purchase_date",
    "data_start_date",
    "data_end_date"
}

RAG_TOOL_NAME = "business_knowledge_search"


def remove_list_markers(text):
    """移除行首编号，避免将列表序号识别为业务数字。"""
    return re.sub(
        r"(?m)^\s*\d+\s*[.、)]\s*",
        "",
        text
    )


def normalize_year_month(text):
    """标准化YYYY-MM中的月份数字，移除月份前导零。"""
    def replace(match):
        year = match.group(1)
        month = str(int(match.group(2)))
        return f"{year} {month}"

    return re.sub(
        r"\b(\d{4})-(\d{1,2})\b",
        replace,
        text
    )


def normalize_number(value):
    """
    Normalize numeric values for grounding comparison.

    Examples:
    534.40 -> 534.4
    3218123.8399999999 -> 3218123.84
    """

    try:
        number = float(value)

        if number.is_integer():
            return str(int(number))

        return (
            f"{number:.2f}"
            .rstrip("0")
            .rstrip(".")
        )

    except Exception:
        return value

def extract_numbers(text):
    """提取文本中的数字并标准化格式。"""
    if not isinstance(text, str):
        return set()

    text = remove_list_markers(text)
    text = normalize_year_month(text)

    numbers = re.findall(
        r"-?\d[\d,]*(?:\.\d+)?",
        text
    )

    return {
        normalize_number(number.replace(",", ""))
        for number in numbers
    }


def collect_evidence_numbers(value, key=None):
    """递归收集结构化证据中的数字。"""
    numbers = set()

    if isinstance(value, bool):
        return numbers

    if isinstance(value, (int, float)):
        numbers.add(normalize_number(str(value)))
        return numbers

    if isinstance(value, str):
        if key in TEXT_NUMERIC_EVIDENCE_KEYS:
            numbers.update(
                extract_numbers(value)
            )

        return numbers

    if isinstance(value, dict):
        for child_key, child_value in value.items():
            numbers.update(
                collect_evidence_numbers(
                    child_value,
                    child_key
                )
            )

        return numbers

    if isinstance(value, (list, tuple)):
        for item in value:
            numbers.update(
                collect_evidence_numbers(
                    item,
                    key
                )
            )

    return numbers


def collect_evidence_texts(value):
    """递归收集证据中的字符串。"""
    texts = set()

    if isinstance(value, str):
        texts.add(value)
        return texts

    if isinstance(value, dict):
        for child_value in value.values():
            texts.update(
                collect_evidence_texts(
                    child_value
                )
            )

        return texts

    if isinstance(value, (list, tuple)):
        for item in value:
            texts.update(
                collect_evidence_texts(item)
            )

    return texts


def has_currency_evidence(value):
    """检查证据中是否明确包含币种字段。"""
    if isinstance(value, dict):
        for key, child_value in value.items():
            if key in {
                "currency",
                "currency_code",
                "currency_symbol"
            }:
                return True

            if has_currency_evidence(child_value):
                return True

    if isinstance(value, (list, tuple)):
        return any(
            has_currency_evidence(item)
            for item in value
        )

    return False


def is_rag_tool_item(item):
    """判断Trace项是否来自RAG知识检索工具。"""
    return (
        isinstance(item, dict)
        and item.get("name") == RAG_TOOL_NAME
    )


def split_tool_evidence(tool_results, tool_calls):
    """将结构化Tool证据与RAG证据分离。"""
    structured_results = [
        item for item in tool_results
        if not is_rag_tool_item(item)
    ]
    rag_results = [
        item for item in tool_results
        if is_rag_tool_item(item)
    ]
    structured_calls = [
        item for item in tool_calls
        if not is_rag_tool_item(item)
    ]
    rag_calls = [
        item for item in tool_calls
        if is_rag_tool_item(item)
    ]

    return (
        structured_results,
        rag_results,
        structured_calls,
        rag_calls
    )


def collect_rag_sources(rag_results):
    """收集RAG最终使用的来源；优先使用Tool显式sources，兼容旧results。"""
    sources = []
    seen = set()

    for item in rag_results:
        result = item.get("result", {})
        data = result.get("data", result)

        source_items = data.get("sources")

        if not isinstance(source_items, list):
            source_items = data.get("results", [])

        for chunk in source_items:
            if not isinstance(chunk, dict):
                continue

            source = {
                "source_file": chunk.get("source_file"),
                "section": chunk.get("section"),
                "language": chunk.get("language"),
                "domain": chunk.get("domain")
            }

            key = (
                source["source_file"],
                source["section"],
                source["language"]
            )

            if key in seen:
                continue

            seen.add(key)
            sources.append(source)

    return sources


def has_rag_evidence(rag_results):
    """检查RAG Tool是否成功返回至少一个知识Chunk。"""
    return bool(
        collect_rag_sources(rag_results)
    )


def collect_rag_evidence_texts(rag_results):
    """只收集RAG Chunk正文，避免score等元数据成为知识证据。"""
    texts = set()

    for item in rag_results:
        result = item.get("result", {})
        data = result.get("data", result)

        for chunk in data.get("results", []):
            content = chunk.get("content")

            if isinstance(content, str) and content:
                texts.add(content)

    return texts


def tools_succeeded(tool_results):
    """检查所有Tool是否执行成功。"""
    for item in tool_results:
        result = item.get("result", {})

        if not result.get("success", False):
            return False

    return True


def remove_evidence_texts(answer, evidence_texts):
    """移除回答中直接引用的证据文本，避免文本中的数字误判。"""
    cleaned_answer = answer

    for text in sorted(
        evidence_texts,
        key=len,
        reverse=True
    ):
        if text:
            cleaned_answer = cleaned_answer.replace(
                text,
                ""
            )

    return cleaned_answer


class GroundingValidator:
    """执行确定性的回答与证据一致性检查。"""

    def validate(
        self,
        answer,
        tool_results,
        tool_calls=None,
        allow_general_knowledge=False
    ):
        tool_calls = tool_calls or []
        warnings = []

        answer_non_empty = (
            isinstance(answer, str)
            and bool(answer.strip())
        )

        if not answer_non_empty:
            warnings.append(
                {
                    "type": "empty_answer",
                    "message": "Agent未生成可展示的自然语言回答。"
                }
            )

        safe_answer = (
            answer
            if isinstance(answer, str)
            else ""
        )

        tool_success = tools_succeeded(
            tool_results
        )

        if not tool_success:
            warnings.append(
                {
                    "type": "tool_failure",
                    "message": "存在Tool执行失败。"
                }
            )

        (
            structured_results,
            rag_results,
            structured_calls,
            rag_calls
        ) = split_tool_evidence(
            tool_results,
            tool_calls
        )

        result_numbers = collect_evidence_numbers(
            structured_results
        )

        argument_numbers = collect_evidence_numbers(
            structured_calls
        )

        evidence_numbers = (
            result_numbers
            | argument_numbers
        )

        evidence_texts = collect_evidence_texts(
            structured_results
        )

        evidence_texts.update(
            collect_evidence_texts(
                structured_calls
            )
        )

        rag_evidence_texts = collect_rag_evidence_texts(
            rag_results
        )

        evidence_texts.update(
            rag_evidence_texts
        )

        rag_tool_used = bool(
            rag_results or rag_calls
        )

        rag_evidence_available = has_rag_evidence(
            rag_results
        )

        retrieved_sources = collect_rag_sources(
            rag_results
        )

        if (
            rag_tool_used
            and not rag_evidence_available
            and not allow_general_knowledge
        ):
            warnings.append(
                {
                    "type": "rag_no_evidence",
                    "message": (
                        "已调用业务知识检索工具，"
                        "但没有返回可用知识证据。"
                    )
                }
            )

        cleaned_answer = remove_evidence_texts(
            safe_answer,
            evidence_texts
        )

        answer_numbers = extract_numbers(
            cleaned_answer
        )

        unsupported_numbers = sorted(
            answer_numbers - evidence_numbers
        )

        if unsupported_numbers:
            warnings.append(
                {
                    "type": "unsupported_numbers",
                    "values": unsupported_numbers,
                    "message": (
                        "回答包含当前证据中没有直接出现的数字。"
                    )
                }
            )

        supports_currency = has_currency_evidence(
            structured_results
        )

        uses_currency = any(
            term in safe_answer
            for term in CURRENCY_TERMS
        )

        if uses_currency and not supports_currency:
            warnings.append(
                {
                    "type": "unsupported_currency",
                    "message": (
                        "回答包含币种或货币单位，"
                        "但Tool Result未提供币种证据。"
                    )
                }
            )

        return {
            "passed": len(warnings) == 0,
            "warnings": warnings,
            "checks": {
                "answer_non_empty": answer_non_empty,
                "tool_success": tool_success,
                "supports_currency": supports_currency,
                "rag_tool_used": rag_tool_used,
                "rag_evidence_available": rag_evidence_available,
                "general_knowledge_allowed": allow_general_knowledge
            },
            "evidence_numbers": sorted(
                evidence_numbers
            ),
            "retrieved_sources": retrieved_sources
        }
