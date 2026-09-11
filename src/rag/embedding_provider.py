import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class SiliconFlowEmbeddingProvider:
    """SiliconFlow Embedding Provider。"""

    def __init__(self, model=None, dimensions=1024):
        api_key = os.getenv("SILICONFLOW_API_KEY")
        model = model or os.getenv("SILICONFLOW_EMBEDDING_MODEL")

        if not api_key:
            raise ValueError(
                "SILICONFLOW_API_KEY is not configured"
            )

        if not model:
            raise ValueError(
                "SILICONFLOW_EMBEDDING_MODEL is not configured"
            )

        self.model = model
        self.dimensions = dimensions
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1"
        )

    def embed_texts(self, texts):
        """批量生成文本Embedding。"""
        if not texts:
            return []

        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
            dimensions=self.dimensions
        )

        return [
            item.embedding
            for item in response.data
        ]

    def embed_query(self, query):
        """生成单条查询Embedding。"""
        embeddings = self.embed_texts([query])

        if not embeddings:
            return None

        return embeddings[0]