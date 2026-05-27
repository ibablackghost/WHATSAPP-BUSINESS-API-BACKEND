from __future__ import annotations

from apps.contacts.models import Contact


class ContactRepository:
    def get_or_create_by_wa_id(
        self,
        organization_id,
        wa_id: str,
        phone_number: str,
        profile_name: str = "",
    ) -> tuple[Contact, bool]:
        return Contact.all_objects.get_or_create(
            organization_id=organization_id,
            wa_id=wa_id,
            defaults={
                "phone_number": phone_number,
                "profile_name": profile_name,
            },
        )

    def get_by_wa_id(self, organization_id, wa_id: str) -> Contact | None:
        try:
            return Contact.all_objects.get(organization_id=organization_id, wa_id=wa_id)
        except Contact.DoesNotExist:
            return None
