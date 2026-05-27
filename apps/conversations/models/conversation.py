from django.conf import settings
from django.db import models

from apps.core.models.base import OrganizationMixin


class Conversation(OrganizationMixin):
    """Live chat conversation thread."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ASSIGNED = "assigned", "Assigned"
        WAITING = "waiting", "Waiting"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Channel(models.TextChoices):
        WHATSAPP = "whatsapp", "WhatsApp"
        BOT = "bot", "Bot"
        AGENT = "agent", "Agent"

    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.CASCADE, related_name="conversations"
    )
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_conversations",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True
    )
    channel = models.CharField(
        max_length=20, choices=Channel.choices, default=Channel.WHATSAPP
    )
    subject = models.CharField(max_length=255, blank=True)
    priority = models.PositiveSmallIntegerField(default=0)
    is_bot_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    last_message_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-last_message_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "assigned_agent"]),
        ]


class Message(OrganizationMixin):
    """Individual message in a conversation."""

    class SenderType(models.TextChoices):
        CONTACT = "contact", "Contact"
        AGENT = "agent", "Agent"
        BOT = "bot", "Bot"
        SYSTEM = "system", "System"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender_type = models.CharField(max_length=10, choices=SenderType.choices)
    sender_id = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    content_type = models.CharField(max_length=20, default="text")
    metadata = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
