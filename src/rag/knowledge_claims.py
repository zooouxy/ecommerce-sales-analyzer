import re


SUPPORTED_DOMAIN = "customer_segmentation"

SECTION_ALIASES = {
    "典型特征": "characteristics",
    "典型特征：": "characteristics",
    "Typical Characteristics": "characteristics",
    "Characteristics": "characteristics",
    "可采取动作": "recommended_actions",
    "可采取动作：": "recommended_actions",
    "Recommended Actions": "recommended_actions",
    "Actions": "recommended_actions"
}


def _normalize_heading(line):
    """清理Markdown标题/强调符号，保留原始语义。"""
    text = line.strip()
    text = re.sub(r"^#{1,6}\s*", "", text)
    text = re.sub(r"^\*\*(.*?)\*\*:?$", r"\1", text)
    text = re.sub(r"^__(.*?)__:?$", r"\1", text)
    return text.strip()


def _extract_list_item(line):
    """提取Markdown列表项正文，不做同义改写。"""
    text = line.strip()

    bullet_match = re.match(r"^[-*+]\s+(.+)$", text)
    if bullet_match:
        return bullet_match.group(1).strip()

    numbered_match = re.match(r"^\d+[.)、]\s*(.+)$", text)
    if numbered_match:
        return numbered_match.group(1).strip()

    return None


def _clean_inline_markdown(text):
    """仅移除常见Markdown强调标记，不改变文字内容。"""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    return text.strip()


def extract_customer_segment_claims(content):
    """从客户分群知识Chunk中提取结构化知识Claims。"""
    if not isinstance(content, str):
        raise TypeError("content must be a string")

    claims = {
        "characteristics": [],
        "recommended_actions": []
    }

    current_claim_type = None

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        normalized_heading = _normalize_heading(line)

        if normalized_heading in SECTION_ALIASES:
            current_claim_type = SECTION_ALIASES[normalized_heading]
            continue

        item = _extract_list_item(line)

        if item is None or current_claim_type is None:
            continue

        claims[current_claim_type].append(
            _clean_inline_markdown(item)
        )

    return claims


def build_knowledge_claim(result):
    """将单条Retriever结果转换为结构化知识Claim。"""
    if not isinstance(result, dict):
        raise TypeError("result must be a dictionary")

    domain = result.get("domain")

    if domain != SUPPORTED_DOMAIN:
        return None

    content = result.get("content", "")
    claims = extract_customer_segment_claims(content)

    if not any(claims.values()):
        return None

    return {
        "source_file": result.get("source_file"),
        "section": result.get("section"),
        "language": result.get("language"),
        "domain": domain,
        "claims": claims
    }


def build_knowledge_claims(retrieval):
    """将Retriever返回结果转换为结构化知识Claims列表。"""
    if not isinstance(retrieval, dict):
        raise TypeError("retrieval must be a dictionary")

    results = retrieval.get("results", [])

    if not isinstance(results, list):
        raise TypeError("retrieval results must be a list")

    claims = []

    for result in results:
        claim = build_knowledge_claim(result)

        if claim is not None:
            claims.append(claim)

    return {
        "query": retrieval.get("query"),
        "preferred_language": retrieval.get("preferred_language"),
        "knowledge_claims": claims
    }
