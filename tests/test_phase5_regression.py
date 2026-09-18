import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import EcommerceAgent
from src.structured_fallback_renderer import StructuredFallbackRenderer


def assert_grounding_passed(trace, question):
    """检查Grounding是否通过且最终回答非空。"""
    assert trace["grounding"]["passed"] is True, (
        f"Grounding failed for question: {question}\n"
        f"{trace['grounding']}"
    )
    assert trace["grounding"]["checks"][
        "answer_non_empty"
    ] is True, (
        f"Grounding accepted an empty answer: {question}"
    )


def get_tool_names(trace):
    """返回实际执行的Tool名称列表。"""
    return [
        item["name"]
        for item in trace["tool_calls"]
    ]


def assert_non_empty_answer(trace, question):
    """检查Agent是否实际返回了非空回答。"""
    answer = trace.get("answer")

    assert isinstance(answer, str) and answer.strip(), (
        f"Empty answer for question: {question}"
    )


class EmptyFinalAnswerProvider:
    """模拟Tool成功后LLM最终返回空文本。"""

    def __init__(self):
        self.call_count = 0

    def chat(self, messages, tools=None):
        self.call_count += 1

        if self.call_count == 1:
            tool_call = SimpleNamespace(
                id="call_customer_segments",
                function=SimpleNamespace(
                    name="customer_segments",
                    arguments='{"segment":"Champions"}'
                )
            )
            message = SimpleNamespace(
                content=None,
                tool_calls=[tool_call]
            )
        else:
            message = SimpleNamespace(
                content="",
                tool_calls=[]
            )

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=message
                )
            ]
        )


class SanitizedToEmptyProvider:
    """模拟LLM返回非空但整段会被Grounding Sanitizer删除的回答。"""

    def __init__(self):
        self.call_count = 0

    def chat(self, messages, tools=None):
        self.call_count += 1

        if self.call_count == 1:
            tool_call = SimpleNamespace(
                id="call_customer_segments",
                function=SimpleNamespace(
                    name="customer_segments",
                    arguments='{"segment":"Champions"}'
                )
            )
            message = SimpleNamespace(
                content=None,
                tool_calls=[tool_call]
            )
        else:
            # 999不在Tool证据中，因此这一整行会被Sanitizer删除。
            message = SimpleNamespace(
                content="Champions客户贡献收入为999。",
                tool_calls=[]
            )

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=message
                )
            ]
        )


def bypass_structured_fast_path_once(agent):
    """
    测试辅助：仅第一次绕过deterministic structured fast path。

    这样可以让测试真正进入第二轮LLM，再分别验证：
    1. Sanitizer清空后的deterministic fallback；
    2. LLM空回答后的deterministic fallback。

    第二次调用StructuredFallback时恢复真实Renderer，
    因此不会削弱fallback本身的测试覆盖。
    """
    original = agent._get_structured_fallback_answer
    call_count = 0

    def wrapped(trace):
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            return None

        return original(trace)

    agent._get_structured_fallback_answer = wrapped


def run_generic_structured_renderer_case():
    """验证Fallback不再只支持customer_segments专用模板。"""
    renderer = StructuredFallbackRenderer()

    print("=" * 70)
    print("CASE: Generic Structured Fallback Renderer")

    sales_result = {
        "success": True,
        "tool": "sales_kpi",
        "data": {
            "total_revenue": 10666684.54,
            "total_orders": 19960,
            "total_quantity": 5588376,
            "average_order_value": 534.4
        }
    }

    sales_answer = renderer.render(
        "sales_kpi",
        sales_result
    )

    assert isinstance(sales_answer, str) and sales_answer.strip()
    assert "10,666,684.54" in sales_answer
    assert "19,960" in sales_answer
    assert "5,588,376" in sales_answer
    assert "534.40" in sales_answer

    comparison_result = {
        "success": True,
        "tool": "product_comparison",
        "data": {
            "entity_type": "product",
            "stock_code_a": "22423",
            "stock_code_b": "85123A",
            "left": {
                "stock_code": "22423",
                "revenue": 174484.74,
                "quantity": 13879
            },
            "right": {
                "stock_code": "85123A",
                "revenue": 106471.28,
                "quantity": 37952
            },
            "comparison": {
                "higher_revenue_product": "22423",
                "higher_quantity_product": "85123A"
            },
            "missing_stock_codes": []
        }
    }

    comparison_answer = renderer.render(
        "product_comparison",
        comparison_result
    )

    assert isinstance(comparison_answer, str) and comparison_answer.strip()
    assert "174,484.74" in comparison_answer
    assert "106,471.28" in comparison_answer
    assert "收入更高的商品：22423" in comparison_answer
    assert "销量更高的商品：85123A" in comparison_answer

    print("PASS")


def run_structured_sanitizer_fallback_case():
    """验证非空LLM回答被Sanitizer清空后，最终fallback能够接管。"""
    question = "Champions客户贡献了多少收入？"
    fallback_agent = EcommerceAgent(
        provider=SanitizedToEmptyProvider()
    )
    bypass_structured_fast_path_once(fallback_agent)

    print("=" * 70)
    print("CASE: Structured Sanitizer Empty Fallback")
    print("QUESTION:")
    print(question)

    trace = fallback_agent.ask_with_trace(question)

    print("\nANSWER:")
    print(trace["answer"])
    print("\nTOOL CALLS:")
    print(trace["tool_calls"])
    print("\nGROUNDING:")
    print(trace["grounding"])

    assert get_tool_names(trace) == ["customer_segments"]
    assert trace.get("grounding_sanitizer_applied") is True
    assert trace.get("answer_mode") == (
        "deterministic_structured_fallback"
    )

    assert_non_empty_answer(trace, question)

    normalized_answer = trace["answer"].replace(",", "")

    for expected_value in [
        "3218123.84",
        "36.11",
        "148",
        "21744.08"
    ]:
        assert expected_value in normalized_answer, (
            f"Missing post-sanitizer fallback fact: {expected_value}"
        )

    assert "999" not in normalized_answer
    assert_grounding_passed(trace, question)

    print("PASS")


def run_structured_empty_answer_fallback_case():
    """验证Structured Tool成功但LLM空响应时启用确定性回退。"""
    question = "Champions客户贡献了多少收入？"
    fallback_agent = EcommerceAgent(
        provider=EmptyFinalAnswerProvider()
    )
    bypass_structured_fast_path_once(fallback_agent)

    print("=" * 70)
    print("CASE: Structured Empty Answer Fallback")
    print("QUESTION:")
    print(question)

    trace = fallback_agent.ask_with_trace(question)

    print("\nANSWER:")
    print(trace["answer"])
    print("\nTOOL CALLS:")
    print(trace["tool_calls"])
    print("\nGROUNDING:")
    print(trace["grounding"])

    assert get_tool_names(trace) == ["customer_segments"]
    assert trace.get("answer_mode") == (
        "deterministic_structured_fallback"
    )

    assert_non_empty_answer(trace, question)

    normalized_answer = trace["answer"].replace(",", "")

    for expected_value in [
        "3218123.84",
        "36.11",
        "148",
        "21744.08"
    ]:
        assert expected_value in normalized_answer, (
            f"Missing fallback fact: {expected_value}"
        )

    assert trace["grounding"]["checks"][
        "answer_non_empty"
    ] is True
    assert_grounding_passed(trace, question)

    print("PASS")


def run_structured_only_case():
    """验证结构化数据查询不会误调用RAG。"""
    question = "Champions客户贡献了多少收入？"

    print("=" * 70)
    print("CASE: Structured-only")
    print("QUESTION:")
    print(question)

    trace = agent.ask_with_trace(question)
    tool_names = get_tool_names(trace)

    print("\nANSWER:")
    print(trace["answer"])
    print("\nTOOL CALLS:")
    print(trace["tool_calls"])
    print("\nGROUNDING:")
    print(trace["grounding"])

    assert tool_names == ["customer_segments"], (
        f"Expected only customer_segments, got {tool_names}"
    )
    assert trace.get("answer_mode") in {
        None,
        "deterministic_structured",
        "deterministic_structured_fallback"
    }, (
        f"Unexpected answer_mode: {trace.get('answer_mode')}"
    )

    assert_non_empty_answer(trace, question)

    normalized_answer = trace["answer"].replace(",", "")

    for expected_value in [
        "3218123.84",
        "36.11",
        "148",
        "21744.08"
    ]:
        assert expected_value in normalized_answer, (
            f"Missing structured fact in answer: {expected_value}"
        )

    evidence_numbers = set(
        trace["grounding"]["evidence_numbers"]
    )
    expected_numbers = {
        "148",
        "21744.08",
        "3218123.84",
        "36.11"
    }

    assert expected_numbers.issubset(evidence_numbers), (
        f"Missing structured evidence: "
        f"{expected_numbers - evidence_numbers}"
    )
    assert_grounding_passed(trace, question)

    print("PASS")


def run_rag_only_case():
    """验证客户分群知识走确定性RAG路径。"""
    question = "Champions客户应该怎么运营？"

    print("=" * 70)
    print("CASE: RAG-only")
    print("QUESTION:")
    print(question)

    trace = agent.ask_with_trace(question)
    tool_names = get_tool_names(trace)

    print("\nANSWER:")
    print(trace["answer"])
    print("\nTOOL CALLS:")
    print(trace["tool_calls"])
    print("\nGROUNDING:")
    print(trace["grounding"])

    assert tool_names == ["business_knowledge_search"], (
        f"Expected only business_knowledge_search, got {tool_names}"
    )
    assert trace.get("answer_mode") == "deterministic_rag", (
        f"Expected deterministic_rag, got "
        f"{trace.get('answer_mode')}"
    )

    assert_non_empty_answer(trace, question)
    answer = trace["answer"]
    assert "优先客户留存" in answer
    assert "提供会员权益或优先体验" in answer
    assert "鼓励推荐与口碑传播" in answer

    sources = trace["grounding"]["retrieved_sources"]

    assert len(sources) == 1, (
        f"Expected one selected source, got {sources}"
    )
    assert sources[0]["section"] == "Champions（冠军客户）", (
        f"Unexpected source: {sources[0]}"
    )
    assert trace["grounding"]["checks"][
        "general_knowledge_allowed"
    ] is False
    assert_grounding_passed(trace, question)

    print("PASS")


def run_hybrid_case():
    """验证结构化事实与RAG知识采用确定性Hybrid组合。"""
    question = "Champions客户贡献了多少收入，并且应该怎么运营？"

    print("=" * 70)
    print("CASE: Hybrid")
    print("QUESTION:")
    print(question)

    trace = agent.ask_with_trace(question)
    tool_names = get_tool_names(trace)

    print("\nANSWER:")
    print(trace["answer"])
    print("\nTOOL CALLS:")
    print(trace["tool_calls"])
    print("\nGROUNDING:")
    print(trace["grounding"])

    assert set(tool_names) == {
        "customer_segments",
        "business_knowledge_search"
    }, (
        f"Unexpected hybrid tools: {tool_names}"
    )
    assert trace.get("answer_mode") == "deterministic_hybrid", (
        f"Expected deterministic_hybrid, got "
        f"{trace.get('answer_mode')}"
    )

    assert_non_empty_answer(trace, question)
    answer = trace["answer"]

    for expected_text in [
        "148",
        "3218123.84",
        "36.11%",
        "21744.08",
        "优先客户留存",
        "提供会员权益或优先体验"
    ]:
        assert expected_text in answer, (
            f"Missing hybrid evidence: {expected_text}"
        )

    sources = trace["grounding"]["retrieved_sources"]

    assert len(sources) == 1, (
        f"Expected one selected source, got {sources}"
    )
    assert sources[0]["section"] == "Champions（冠军客户）", (
        f"Unexpected source: {sources[0]}"
    )
    assert trace.get("grounding_sanitizer_applied") is None
    assert trace["grounding"]["checks"][
        "general_knowledge_allowed"
    ] is False
    assert_grounding_passed(trace, question)

    print("PASS")


def run_general_suggestions_case():
    """验证模型通用建议与知识库内容显式区分。"""
    question = "除了知识库里的策略，还有哪些通用运营建议？"

    print("=" * 70)
    print("CASE: General Suggestions")
    print("QUESTION:")
    print(question)

    trace = agent.ask_with_trace(question)
    tool_names = get_tool_names(trace)

    print("\nANSWER:")
    print(trace["answer"])
    print("\nTOOL CALLS:")
    print(trace["tool_calls"])
    print("\nGROUNDING:")
    print(trace["grounding"])

    assert tool_names == ["business_knowledge_search"], (
        f"Expected business_knowledge_search, got {tool_names}"
    )
    assert trace.get("answer_mode") is None, (
        f"Unexpected answer_mode: {trace.get('answer_mode')}"
    )
    assert trace.get("provenance_normalization_applied") is True, (
        "Expected provenance normalization to be applied"
    )

    assert_non_empty_answer(trace, question)
    answer = trace["answer"]

    assert "**通用建议（非知识库内容）**" in answer
    assert "来自模型通用电商知识" in answer
    assert "不属于当前知识库检索内容" in answer

    assert trace["grounding"]["checks"][
        "general_knowledge_allowed"
    ] is True
    assert_grounding_passed(trace, question)

    print("PASS")


def run_phase4_regression_case():
    """确认Phase 5改动未破坏Phase 4商品对比能力。"""
    question = "商品22423和85123A相比，哪个收入更高，哪个销量更高？"

    print("=" * 70)
    print("CASE: Phase 4 Regression")
    print("QUESTION:")
    print(question)

    trace = agent.ask_with_trace(question)
    tool_names = get_tool_names(trace)

    print("\nANSWER:")
    print(trace["answer"])
    print("\nTOOL CALLS:")
    print(trace["tool_calls"])
    print("\nGROUNDING:")
    print(trace["grounding"])

    assert tool_names == ["product_comparison"], (
        f"Expected only product_comparison, got {tool_names}"
    )

    assert_non_empty_answer(trace, question)
    answer = trace["answer"]

    assert "22423" in answer
    assert "85123A" in answer

    tool_data = trace["tool_results"][0]["result"]["data"]
    comparison = tool_data["comparison"]

    assert comparison["higher_revenue_product"] == "22423", (
        "Expected 22423 to have higher revenue"
    )
    assert comparison["higher_quantity_product"] == "85123A", (
        "Expected 85123A to have higher quantity"
    )

    assert_grounding_passed(trace, question)

    print("PASS")


def main():
    run_generic_structured_renderer_case()
    run_structured_sanitizer_fallback_case()
    run_structured_empty_answer_fallback_case()
    run_structured_only_case()
    run_rag_only_case()
    run_hybrid_case()
    run_general_suggestions_case()
    run_phase4_regression_case()

    print("=" * 70)
    print("ALL PHASE 5 AGENT REGRESSION TESTS PASSED")


if __name__ == "__main__":
    agent = EcommerceAgent()
    main()
