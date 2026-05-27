from django.db import models

from apps.core.models.base import OrganizationMixin


class PaymentTransaction(OrganizationMixin):
    """Mobile Money payment transaction."""

    class Provider(models.TextChoices):
        WAVE = "wave", "Wave"
        ORANGE_MONEY = "orange_money", "Orange Money"
        FREE_MONEY = "free_money", "Free Money"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.CASCADE, related_name="payments"
    )
    conversation = models.ForeignKey(
        "conversations.Conversation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    provider = models.CharField(max_length=20, choices=Provider.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="XOF")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    external_id = models.CharField(max_length=100, blank=True, db_index=True)
    payment_url = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "provider"]),
        ]
