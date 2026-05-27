from django.db import models

from apps.core.models.base import OrganizationMixin


class FAQEntry(OrganizationMixin):
    """FAQ knowledge base entry with vector embedding for RAG (JSON, compatible SQLite)."""

    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=10, default="fr")
    embedding = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "FAQ entries"
        indexes = [
            models.Index(fields=["organization", "language", "is_active"]),
        ]


class ConversationMemory(OrganizationMixin):
    """Short-term conversation memory for AI context."""

    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.CASCADE, related_name="ai_memories"
    )
    role = models.CharField(max_length=20)
    content = models.TextField()
    sentiment = models.CharField(max_length=20, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name_plural = "Conversation memories"
