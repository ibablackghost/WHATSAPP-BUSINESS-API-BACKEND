"""Base models and multi-tenancy primitives."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from django.db import models

from apps.core.models.managers import OrganizationManager, OrganizationQuerySet

if TYPE_CHECKING:
    from apps.organizations.models import Organization


class UUIDModel(models.Model):
    """Abstract model with UUID primary key."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    """Abstract model with created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrganizationMixin(UUIDModel, TimestampedModel):
    """
    Multi-tenant mixin — all tenant-scoped models must inherit this.
    Automatically filters queries by current organization.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        db_index=True,
    )

    objects = OrganizationManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["organization", "created_at"]),
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        from apps.core.middleware.organization import get_current_organization

        if not self.organization_id:
            org = get_current_organization()
            if org:
                self.organization = org
        super().save(*args, **kwargs)


# Re-export for convenience
OrganizationQuerySet = OrganizationQuerySet
