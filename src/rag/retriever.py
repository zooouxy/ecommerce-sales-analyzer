import re

from src.rag.vector_store import LocalVectorStore


LOW_VALUE_SECTIONS = {
    "purpose",
    "用途"
}


class KnowledgeRetriever:
    """知识库检索层。"""

    def __init__(self, vector_store=None):
        self.vector_store = (
            vector_store
            or LocalVectorStore()
        )

    def retrieve(self, query, top_k=3):
        """检索知识，并进行语言偏好、低价值过滤和重复结果处理。"""
        if not query or not query.strip():
            raise ValueError(
                "Query must not be empty"
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be at least 1"
            )

        preferred_language = self._detect_language(
            query
        )

        candidate_k = max(
            top_k * 4,
            10
        )

        candidates = self.vector_store.search(
            query=query,
            top_k=candidate_k
        )

        candidates = [
            item
            for item in candidates
            if not self._is_low_value_section(
                item["section"]
            )
        ]

        results = self._deduplicate(
            candidates=candidates,
            preferred_language=preferred_language
        )

        return {
            "query": query,
            "preferred_language": preferred_language,
            "results": results[:top_k]
        }

    def _detect_language(self, text):
        """根据查询文本判断主要语言。"""
        if re.search(
            r"[\u4e00-\u9fff]",
            text
        ):
            return "zh"

        return "en"

    def _normalize_section(self, section):
        """标准化Section，用于识别同一文档中的双语重复知识点。"""
        section = re.sub(
            r"（.*?）",
            "",
            section
        )

        section = re.sub(
            r"\(.*?\)",
            "",
            section
        )

        return section.strip().lower()

    def _is_low_value_section(self, section):
        """识别不适合作为检索结果的说明性Section。"""
        return (
            section.strip().lower()
            in LOW_VALUE_SECTIONS
        )

    def _deduplicate(
        self,
        candidates,
        preferred_language
    ):
        """去除同一文档中的双语重复Section。"""
        grouped = {}

        for item in candidates:
            key = (
                item["source_file"],
                self._normalize_section(
                    item["section"]
                )
            )

            existing = grouped.get(key)

            if existing is None:
                grouped[key] = item
                continue

            existing_is_preferred = (
                existing["language"]
                == preferred_language
            )

            current_is_preferred = (
                item["language"]
                == preferred_language
            )

            if (
                current_is_preferred
                and not existing_is_preferred
            ):
                grouped[key] = item
                continue

            if (
                current_is_preferred
                == existing_is_preferred
                and item["score"] > existing["score"]
            ):
                grouped[key] = item

        results = list(
            grouped.values()
        )

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results