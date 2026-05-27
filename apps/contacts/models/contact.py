from django.db import models

from apps.core.models.base import OrganizationMixin


class ContactTag(OrganizationMixin):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#3B82F6")

    class Meta:
        unique_together = [("organization", "name")]


class Contact(OrganizationMixin):
    """WhatsApp contact within an organization."""

    wa_id = models.CharField(max_length=20, db_index=True)
    phone_number = models.CharField(max_length=20, db_index=True)
    profile_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    tags = models.ManyToManyField(ContactTag, blank=True, related_name="contacts")
    is_blocked = models.BooleanField(default=False)
    language = models.CharField(max_length=10, blank=True)
    last_interaction_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("organization", "wa_id")]
        indexes = [
            models.Index(fields=["organization", "phone_number"]),
        ]
