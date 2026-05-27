from django.db import models

from apps.core.models.base import OrganizationMixin


class BotFlow(OrganizationMixin):
    """Conversation flow definition (USSD-style)."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    default_language = models.CharField(max_length=10, default="fr")
    session_timeout_minutes = models.PositiveIntegerField(default=30)
    fallback_text = models.JSONField(
        default=dict,
        help_text='{"fr": "Je n\'ai pas compris", "en": "I did not understand"}',
    )
    max_invalid_retries = models.PositiveSmallIntegerField(default=3)

    class Meta:
        unique_together = [("organization", "slug")]


class BotStep(OrganizationMixin):
    """Single node in a conversation flow."""

    class NodeType(models.TextChoices):
        MESSAGE = "message", "Message"
        MENU = "menu", "Menu"
        CONDITION = "condition", "Condition"
        API_CALL = "api_call", "API Call"
        AI = "ai", "AI"
        PAYMENT = "payment", "Payment"
        ASSIGN_AGENT = "assign_agent", "Assign Agent"
        END = "end", "End"

    flow = models.ForeignKey(BotFlow, on_delete=models.CASCADE, related_name="steps")
    key = models.CharField(max_length=100)
    node_type = models.CharField(max_length=20, choices=NodeType.choices)
    config = models.JSONField(default=dict)
    next_step_key = models.CharField(max_length=100, blank=True)
    translations = models.JSONField(default=dict)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    is_entry = models.BooleanField(default=False)

    class Meta:
        unique_together = [("flow", "key")]
        ordering = ["created_at"]


class SessionState(OrganizationMixin):
    """Per-contact flow session state."""

    flow = models.ForeignKey(BotFlow, on_delete=models.CASCADE, related_name="sessions")
    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.CASCADE, related_name="bot_sessions"
    )
    conversation = models.ForeignKey(
        "conversations.Conversation",
        on_delete=models.CASCADE,
        related_name="bot_sessions",
    )
    current_step_key = models.CharField(max_length=100)
    context_variables = models.JSONField(default=dict)
    invalid_input_count = models.PositiveSmallIntegerField(default=0)
    language = models.CharField(max_length=10, default="fr")
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "contact", "is_active"]),
        ]
