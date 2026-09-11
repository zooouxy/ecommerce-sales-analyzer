import re


def _section_aliases(section):
    """从分群Section中提取英文名和中文括号名。"""
    if not isinstance(section, str):
        return []

    section = section.strip()

    if not section:
        return []

    aliases = []

    match = re.match(r"^(.*?)（(.*?)）$", section)

    if match:
        english_name = match.group(1).strip()
        chinese_name = match.group(2).strip()

        if english_name:
            aliases.append(english_name)

        if chinese_name:
            aliases.append(chinese_name)
    else:
        aliases.append(section)

    return aliases


def _query_mentions_section(query, section):
    """判断用户问题是否明确提到指定知识Section。"""
    if not isinstance(query, str):
        return False

    normalized_query = query.casefold()

    for alias in _section_aliases(section):
        if alias.casefold() in normalized_query:
            return True

    return False


def select_knowledge_claims(claims_payload):
    """优先选择用户问题明确提到的知识实体，否则保留候选结果。"""
    if not isinstance(claims_payload, dict):
        raise TypeError("claims_payload must be a dictionary")

    query = claims_payload.get("query", "")
    knowledge_claims = claims_payload.get("knowledge_claims", [])

    if not isinstance(knowledge_claims, list):
        raise TypeError("knowledge_claims must be a list")

    explicit_matches = [
        claim
        for claim in knowledge_claims
        if _query_mentions_section(
            query,
            claim.get("section")
        )
    ]

    selected_claims = (
        explicit_matches
        if explicit_matches
        else knowledge_claims
    )

    return {
        "query": query,
        "preferred_language": claims_payload.get("preferred_language"),
        "knowledge_claims": selected_claims
    }
