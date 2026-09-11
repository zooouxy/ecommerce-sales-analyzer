def _render_list(items):
    """将Claims列表稳定渲染为Markdown列表。"""
    return "\n".join(f"- {item}" for item in items)


def render_customer_segment_claim(claim):
    """将单条客户分群Claim确定性渲染为Markdown文本。"""
    if not isinstance(claim, dict):
        raise TypeError("claim must be a dictionary")

    claims = claim.get("claims", {})
    characteristics = claims.get("characteristics", [])
    recommended_actions = claims.get("recommended_actions", [])

    if not characteristics and not recommended_actions:
        return ""

    section = claim.get("section") or "Customer Segment"

    parts = [f"根据知识库，{section}："]

    if characteristics:
        parts.extend([
            "",
            "**典型特征**",
            _render_list(characteristics)
        ])

    if recommended_actions:
        parts.extend([
            "",
            "**知识库建议**",
            _render_list(recommended_actions)
        ])

    return "\n".join(parts)


def render_knowledge_claims(claims_payload):
    """渲染结构化知识Claims；当前仅支持客户分群知识。"""
    if not isinstance(claims_payload, dict):
        raise TypeError("claims_payload must be a dictionary")

    knowledge_claims = claims_payload.get("knowledge_claims", [])

    if not isinstance(knowledge_claims, list):
        raise TypeError("knowledge_claims must be a list")

    rendered = []

    for claim in knowledge_claims:
        if claim.get("domain") != "customer_segmentation":
            continue

        text = render_customer_segment_claim(claim)

        if text:
            rendered.append({
                "source_file": claim.get("source_file"),
                "section": claim.get("section"),
                "language": claim.get("language"),
                "domain": claim.get("domain"),
                "text": text
            })

    return {
        "query": claims_payload.get("query"),
        "preferred_language": claims_payload.get("preferred_language"),
        "rendered_knowledge": rendered
    }
