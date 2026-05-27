from django.db import models

from apps.core.models.base import OrganizationMixin


class NotificationCampaign(OrganizationMixin):
    """Scheduled WhatsApp notification campaign."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    name = models.CharField(max_length=255)
    template_name = models.CharField(max_length=100)
    template_language = models.CharField(max_length=10, default="fr")
    template_components = models.JSONField(default=list)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_recipients = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    read_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    filter_tags = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-created_at"]


class CampaignRecipient(OrganizationMixin):
    campaign = models.ForeignKey(
        NotificationCampaign, on_delete=models.CASCADE, related_name="recipients"
    )
    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.CASCADE, related_name="campaigns"
    )
    status = models.CharField(max_length=20, default="pending")
    wa_message_id = models.CharField(max_length=100, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        unique_together = [("campaign", "contact")]
