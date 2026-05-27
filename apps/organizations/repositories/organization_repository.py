from __future__ import annotations

from uuid import UUID

from apps.organizations.models import Organization


class OrganizationRepository:
    def get_by_id(self, org_id: UUID) -> Organization | None:
        try:
            return Organization.objects.get(id=org_id, is_active=True)
        except Organization.DoesNotExist:
            return None

    def get_by_slug(self, slug: str) -> Organization | None:
        try:
            return Organization.objects.get(slug=slug, is_active=True)
        except Organization.DoesNotExist:
            return None

    def create(self, *, name: str, slug: str, plan: str) -> Organization:
        return Organization.objects.create(name=name, slug=slug, plan=plan)
