"""RAG semantic search over FAQ entries."""
from __future__ import annotations

import math
from uuid import UUID

from apps.ai.models import FAQEntry
from apps.ai.services.embedding_service import EmbeddingService


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return -1.0
    return dot / (norm_a * norm_b)


class RAGService:
    def __init__(self) -> None:
        self._embedder = EmbeddingService()

    def search(
        self, organization_id: UUID, query: str, language: str = "fr", limit: int = 5
    ) -> list[FAQEntry]:
        query_embedding = self._embedder.embed(query)
        candidates = FAQEntry.all_objects.filter(
            organization_id=organization_id,
            language=language,
            is_active=True,
            embedding__isnull=False,
        )
        scored: list[tuple[float, FAQEntry]] = []
        for faq in candidates:
            if isinstance(faq.embedding, list):
                score = _cosine_similarity(query_embedding, faq.embedding)
                scored.append((score, faq))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [faq for _, faq in scored[:limit]]

    def index_faq(self, faq: FAQEntry) -> FAQEntry:
        text = f"{faq.question}\n{faq.answer}"
        faq.embedding = self._embedder.embed(text)
        faq.save(update_fields=["embedding", "updated_at"])
        return faq
