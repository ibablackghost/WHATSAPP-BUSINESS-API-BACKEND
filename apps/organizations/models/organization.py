"""Organization and membership models."""
from django.conf import settings
from django.db import models

from apps.core.models.base import UUIDModel, TimestampedModel


class Organization(UUIDModel, TimestampedModel):
    """Tenant root entity."""

    class Plan(models.TextChoices):
        FREE = "free", "Free"
        STARTER = "starter", "Starter"
        BUSINESS = "business", "Business"
        ENTERPRISE = "enterprise", "Enterprise"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.FREE)
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)
    # WhatsApp Business credentials (encrypted)
    whatsapp_phone_number_id = models.CharField(max_length=50, blank=True)
    whatsapp_business_account_id = models.CharField(max_length=50, blank=True)
    whatsapp_access_token_encrypted = models.TextField(blank=True)
    timezone = models.CharField(max_length=50, default="Africa/Dakar")
    default_language = models.CharField(max_length=10, default="fr")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class OrganizationMembership(UUIDModel, TimestampedModel):
    """Links users to organizations with roles."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        SUPERVISOR = "supervisor", "Supervisor"
        AGENT = "agent", "Agent"

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.AGENT)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = [("organization", "user")]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]
