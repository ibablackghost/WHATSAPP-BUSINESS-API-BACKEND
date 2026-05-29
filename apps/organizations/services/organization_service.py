"""Organization business logic."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from django.db import transaction

from apps.core.services.encryption import encryption_service
from apps.organizations.models import Organization, OrganizationMembership
from apps.organizations.repositories.organization_repository import (
    OrganizationRepository,
)

if TYPE_CHECKING:
    from apps.accounts.models import User

logger = logging.getLogger(__name__)


class OrganizationService:
    def __init__(self) -> None:
        self._repo = OrganizationRepository()

    @transaction.atomic
    def create_organization(
        self,
        *,
        name: str,
        slug: str,
        owner: User,
        plan: str = Organization.Plan.FREE,
    ) -> Organization:
        org = self._repo.create(name=name, slug=slug, plan=plan)
        OrganizationMembership.objects.create(
            organization=org,
            user=owner,
            role=OrganizationMembership.Role.ADMIN,
            is_default=True,
        )
        return org

    def set_whatsapp_credentials(
        self,
        organization: Organization,
        *,
        phone_number_id: str,
        business_account_id: str,
        access_token: str,
    ) -> Organization:
        cleaned_token = (access_token or "").strip()
        if cleaned_token.lower().startswith("bearer "):
            cleaned_token = cleaned_token[7:].strip()
        organization.whatsapp_phone_number_id = phone_number_id
        organization.whatsapp_business_account_id = business_account_id
        organization.whatsapp_access_token_encrypted = encryption_service.encrypt(
            cleaned_token
        )
        organization.save(
            update_fields=[
                "whatsapp_phone_number_id",
                "whatsapp_business_account_id",
                "whatsapp_access_token_encrypted",
                "updated_at",
            ]
        )
        return organization

    def get_access_token(self, organization: Organization) -> str:
        if not organization.whatsapp_access_token_encrypted:
            return ""
        try:
            return encryption_service.decrypt(organization.whatsapp_access_token_encrypted)
        except ValueError:
            logger.error(
                "Impossible de déchiffrer le token WhatsApp pour org %s — "
                "refaire whatsapp-config",
                organization.id,
            )
            return ""

    def get_by_id(self, org_id: UUID) -> Organization | None:
        return self._repo.get_by_id(org_id)
