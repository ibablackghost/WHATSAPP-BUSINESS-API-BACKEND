from django.db import models

from apps.core.models.base import OrganizationMixin


class WhatsAppMessageLog(OrganizationMixin):
    """Outbound/inbound WhatsApp message audit log."""

    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"

    class MessageType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        AUDIO = "audio", "Audio"
        VIDEO = "video", "Video"
        DOCUMENT = "document", "Document"
        LOCATION = "location", "Location"
        INTERACTIVE = "interactive", "Interactive"
        TEMPLATE = "template", "Template"
        BUTTON = "button", "Button"
        LIST = "list", "List"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        READ = "read", "Read"
        FAILED = "failed", "Failed"

    wa_message_id = models.CharField(max_length=100, blank=True, db_index=True)
    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.CASCADE, related_name="wa_messages"
    )
    conversation = models.ForeignKey(
        "conversations.Conversation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wa_messages",
    )
    direction = models.CharField(max_length=10, choices=Direction.choices)
    message_type = models.CharField(max_length=20, choices=MessageType.choices)
    content = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "wa_message_id"]),
            models.Index(fields=["organization", "status"]),
        ]


class WhatsAppTemplate(OrganizationMixin):
    """Approved WhatsApp message template."""

    name = models.CharField(max_length=100)
    language = models.CharField(max_length=10, default="fr")
    category = models.CharField(max_length=50)
    components = models.JSONField(default=list)
    status = models.CharField(max_length=20, default="APPROVED")
    meta_template_id = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = [("organization", "name", "language")]
