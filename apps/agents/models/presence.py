from django.conf import settings
from django.db import models

from apps.core.models.base import OrganizationMixin


class AgentPresence(OrganizationMixin):
    """Real-time agent online status."""

    class Status(models.TextChoices):
        ONLINE = "online", "Online"
        AWAY = "away", "Away"
        BUSY = "busy", "Busy"
        OFFLINE = "offline", "Offline"

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="presences",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.OFFLINE
    )
    active_conversations = models.PositiveIntegerField(default=0)
    max_conversations = models.PositiveIntegerField(default=5)
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("organization", "agent")]
