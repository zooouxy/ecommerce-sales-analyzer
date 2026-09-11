import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import EcommerceAgent


def assert_grounding_passed(trace, question):
    """检查Grounding是否通过。"""
    assert trace["grounding"]["passed"] is True, (
        f"Grounding failed for question: {question}\n"
        f"{trace['grounding']}"
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
    assert trace.get("answer_mode") is None, (
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
        "rag_evidence_available"
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
