import json
from pathlib import Path

import numpy as np

from src.rag.embedding_provider import SiliconFlowEmbeddingProvider
from src.rag.knowledge_loader import load_knowledge_base


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX_PATH = PROJECT_ROOT / "data" / "rag_index.json"


def cosine_similarity(query_vector, matrix):
    """计算查询向量与Embedding矩阵的余弦相似度。"""
    query_vector = np.asarray(
        query_vector,
        dtype=np.float32
    )

    matrix = np.asarray(
        matrix,
        dtype=np.float32
    )

    query_norm = np.linalg.norm(query_vector)
    matrix_norms = np.linalg.norm(
        matrix,
        axis=1
    )

    denominator = matrix_norms * query_norm

    denominator = np.where(
        denominator == 0,
        1e-12,
        denominator
    )

    return (
        matrix @ query_vector
    ) / denominator


class LocalVectorStore:
    """基于NumPy的轻量本地向量检索。"""

    def __init__(
        self,
        embedding_provider=None,
        index_path=DEFAULT_INDEX_PATH
    ):
        self.embedding_provider = (
            embedding_provider
            or SiliconFlowEmbeddingProvider()
        )

        self.index_path = Path(index_path)
        self.chunks = []
        self.embeddings = None

    def build_index(self):
        """读取知识库并生成Embedding索引。"""
        chunks = load_knowledge_base()

        if not chunks:
            raise ValueError(
                "No knowledge chunks found"
            )

        texts = [
            self._chunk_to_embedding_text(chunk)
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_provider.embed_texts(
                texts
            )
        )

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Embedding count does not match chunk count"
            )

        self.chunks = chunks
        self.embeddings = np.asarray(
            embeddings,
            dtype=np.float32
        )

        self._save_index()

        return {
            "chunk_count": len(self.chunks),
            "embedding_dimension": (
                self.embeddings.shape[1]
            )
        }

    def load_index(self):
        """从本地文件加载已有索引。"""
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"RAG index not found: {self.index_path}"
            )

        data = json.loads(
            self.index_path.read_text(
                encoding="utf-8"
            )
        )

        self.chunks = data["chunks"]
        self.embeddings = np.asarray(
            data["embeddings"],
            dtype=np.float32
        )

        return {
            "chunk_count": len(self.chunks),
            "embedding_dimension": (
                self.embeddings.shape[1]
            )
        }

    def search(self, query, top_k=3):
        """按余弦相似度检索最相关知识Chunk。"""
        if not query or not query.strip():
            raise ValueError(
                "Query must not be empty"
            )

        if self.embeddings is None:
            self.load_index()

        query_embedding = (
            self.embedding_provider.embed_query(
                query
            )
        )

        scores = cosine_similarity(
            query_embedding,
            self.embeddings
        )

        top_k = min(
            top_k,
            len(self.chunks)
        )

        top_indices = np.argsort(
            scores
        )[::-1][:top_k]

        results = []

        for index in top_indices:
            chunk = self.chunks[int(index)]

            results.append(
                {
                    **chunk,
                    "score": round(
                        float(scores[index]),
                        6
                    )
                }
            )

        return results

    def _chunk_to_embedding_text(self, chunk):
        """将Chunk转换为Embedding输入文本。"""
        return (
            f"Domain: {chunk['domain']}\n"
            f"Language: {chunk['language']}\n"
            f"Section: {chunk['section']}\n"
            f"Content:\n{chunk['content']}"
        )

    def _save_index(self):
        """保存Chunk和Embedding到本地JSON。"""
        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {
            "chunks": self.chunks,
            "embeddings": (
                self.embeddings.tolist()
            )
        }

        self.index_path.write_text(
            json.dumps(
                data,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )