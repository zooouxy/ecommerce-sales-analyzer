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
    "last_purchase_date"
}


def remove_list_markers(text):
    """移除行首编号，避免将列表序号识别为业务数字。"""
    return re.sub(
        r"(?m)^\s*\d+\s*[.、)]\s*",
        "",
        text
    )


def extract_numbers(text):
    """提取文本中的数字并标准化格式。"""
    if not isinstance(text, str):
        return set()

    text = remove_list_markers(text)

    text = re.sub(
        r"\b(\d{4})-(\d{1,2})\b",
        r"\1 \2",
        text
    )

    numbers = re.findall(
        r"-?\d[\d,]*(?:\.\d+)?",
        text
    )

    return {
        number.replace(",", "")
        for number in numbers
    }


def collect_evidence_numbers(value, key=None):
    """递归收集结构化证据中的数字。"""
    numbers = set()

    if isinstance(value, bool):
        return numbers

    if isinstance(value, (int, float)):
        numbers.add(str(value))
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
        tool_calls=None
    ):
        tool_calls = tool_calls or []

        warnings = []

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

        result_numbers = collect_evidence_numbers(
            tool_results
        )

        argument_numbers = collect_evidence_numbers(
            tool_calls
        )

        evidence_numbers = (
            result_numbers
            | argument_numbers
        )

        evidence_texts = collect_evidence_texts(
            tool_results
        )

        evidence_texts.update(
            collect_evidence_texts(
                tool_calls
            )
        )

        cleaned_answer = remove_evidence_texts(
            answer,
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
            tool_results
        )

        uses_currency = any(
            term in answer
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
                "tool_success": tool_success,
                "supports_currency": supports_currency
            },
            "evidence_numbers": sorted(
                evidence_numbers
            )
        }