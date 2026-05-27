"""AI chat with RAG, memory, sentiment, guardrails."""
from __future__ import annotations

from uuid import UUID

from django.conf import settings
from openai import OpenAI

from apps.ai.models import ConversationMemory, FAQEntry
from apps.ai.services.rag_service import RAGService

SYSTEM_PROMPT = """Tu es l'assistant WhatBot Pro pour le service client.
Réponds en français de manière professionnelle et concise.
Utilise uniquement les informations du contexte FAQ fourni.
Si tu ne sais pas, propose de transférer à un agent humain.
Ne partage jamais de données personnelles ou confidentielles.
"""

GUARDRAIL_BLOCKED = [
    "mot de passe",
    "password",
    "carte bancaire",
    "credit card",
    "numéro de sécurité sociale",
]


class ChatService:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._rag = RAGService()

    def generate_response(
        self,
        organization_id: UUID,
        contact_id: UUID,
        message: str,
        language: str = "fr",
    ) -> dict:
        if self._violates_guardrails(message):
            return {
                "text": "Je ne peux pas traiter cette demande. Un agent va vous assister.",
                "escalate": True,
            }

        faq_context = self._build_faq_context(organization_id, message, language)
        history = self._get_memory(organization_id, contact_id)
        sentiment = self._analyze_sentiment(message)

        ConversationMemory.all_objects.create(
            organization_id=organization_id,
            contact_id=contact_id,
            role="user",
            content=message,
            sentiment=sentiment,
        )

        messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + faq_context}]
        for mem in history[-10:]:
            messages.append({"role": mem.role, "content": mem.content})
        messages.append({"role": "user", "content": message})

        response = self._client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.3,
        )
        text = response.choices[0].message.content or ""

        ConversationMemory.all_objects.create(
            organization_id=organization_id,
            contact_id=contact_id,
            role="assistant",
            content=text,
        )

        escalate = sentiment in ("negative", "angry") or "agent" in text.lower()
        return {"text": text, "escalate": escalate, "sentiment": sentiment}

    def _build_faq_context(
        self, organization_id: UUID, query: str, language: str
    ) -> str:
        entries = self._rag.search(organization_id, query, language)
        if not entries:
            return "Aucun contexte FAQ disponible."
        parts = []
        for e in entries:
            parts.append(f"Q: {e.question}\nR: {e.answer}")
        return "Contexte FAQ:\n" + "\n---\n".join(parts)

    def _get_memory(self, organization_id: UUID, contact_id: UUID) -> list:
        return list(
            ConversationMemory.all_objects.filter(
                organization_id=organization_id,
                contact_id=contact_id,
            ).order_by("-created_at")[:20]
        )[::-1]

    def _analyze_sentiment(self, text: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Classify sentiment as: positive, neutral, negative, angry. Reply with one word only.",
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=10,
            )
            return (response.choices[0].message.content or "neutral").strip().lower()
        except Exception:
            return "neutral"

    @staticmethod
    def _violates_guardrails(text: str) -> bool:
        lower = text.lower()
        return any(term in lower for term in GUARDRAIL_BLOCKED)
