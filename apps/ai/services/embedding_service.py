"""OpenAI embedding service."""
from __future__ import annotations

from django.conf import settings
from openai import OpenAI


class EmbeddingService:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
