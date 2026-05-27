"""Organization-scoped queryset and manager."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db import models

if TYPE_CHECKING:
    from apps.organizations.models import Organization


class OrganizationQuerySet(models.QuerySet):
    """QuerySet that enforces organization filtering."""

    def for_organization(self, organization: Organization) -> OrganizationQuerySet:
        return self.filter(organization=organization)

    def active(self) -> OrganizationQuerySet:
        return self.filter(is_active=True) if hasattr(self.model, "is_active") else self


class OrganizationManager(models.Manager.from_queryset(OrganizationQuerySet)):  # type: ignore[misc]
    """Manager that auto-filters by current organization context."""

    def get_queryset(self) -> OrganizationQuerySet:
        qs = super().get_queryset()
        from apps.core.middleware.organization import get_current_organization

        org = get_current_organization()
        if org is not None:
            return qs.filter(organization=org)
        return qs.none()

    def unsafe_all(self) -> OrganizationQuerySet:
        """Bypass tenant filter — use only in system tasks with explicit org."""
        return super().get_queryset()
