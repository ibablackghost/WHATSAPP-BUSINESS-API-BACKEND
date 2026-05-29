"""Process incoming WhatsApp webhooks."""
from __future__ import annotations

import logging
from typing import Any

from apps.contacts.repositories.contact_repository import ContactRepository
from apps.conversations.services.conversation_service import ConversationService
from apps.core.middleware.organization import set_current_organization
from apps.core.services.events import DomainEvent, event_bus
from apps.organizations.repositories.organization_repository import (
    OrganizationRepository,
)
from apps.whatsapp.services.message_service import MessageService

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self) -> None:
        self._org_repo = OrganizationRepository()
        self._contact_repo = ContactRepository()
        self._message_service = MessageService()
        self._conversation_service = ConversationService()

    def process_payload(self, payload: dict[str, Any]) -> None:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                metadata = value.get("metadata", {})
                phone_number_id = metadata.get("phone_number_id")
                if not phone_number_id:
                    continue
                org = self._resolve_organization(phone_number_id)
                if not org:
                    logger.warning("Unknown phone_number_id: %s", phone_number_id)
                    continue
                set_current_organization(org)
                try:
                    if "messages" in value:
                        self._process_messages(org, value["messages"], value.get("contacts", []))
                    if "statuses" in value:
                        self._process_statuses(org, value["statuses"])
                finally:
                    set_current_organization(None)

    def _resolve_organization(self, phone_number_id: str):
        from apps.organizations.models import Organization

        qs = Organization.objects.filter(
            whatsapp_phone_number_id=phone_number_id,
            is_active=True,
        )
        if not qs.exists():
            return None
        if qs.count() > 1:
            logger.warning(
                "Plusieurs orgs pour phone_number_id=%s — utilisation de la plus récente",
                phone_number_id,
            )
        return qs.order_by("-updated_at").first()

    def _process_messages(
        self, org, messages: list, contacts_meta: list
    ) -> None:
        contacts_map = {c["wa_id"]: c for c in contacts_meta}
        for msg in messages:
            wa_id = msg.get("from", "")
            meta = contacts_map.get(wa_id, {})
            contact, _ = self._contact_repo.get_or_create_by_wa_id(
                organization_id=org.id,
                wa_id=wa_id,
                phone_number=wa_id,
                profile_name=meta.get("profile", {}).get("name", ""),
            )
            conversation = self._conversation_service.get_or_create_for_contact(
                org, contact
            )
            parsed = self._parse_message(msg)
            self._message_service.record_inbound(
                organization=org,
                contact=contact,
                conversation=conversation,
                wa_message_id=msg.get("id", ""),
                message_type=parsed["type"],
                content=parsed["content"],
            )
            event_bus.publish(
                DomainEvent(
                    event_type="whatsapp.message.received",
                    organization_id=org.id,
                    payload={
                        "contact_id": str(contact.id),
                        "conversation_id": str(conversation.id),
                        "message": parsed,
                    },
                )
            )

    def _process_statuses(self, org, statuses: list) -> None:
        for status in statuses:
            self._message_service.update_status(
                organization_id=org.id,
                wa_message_id=status.get("id", ""),
                status=status.get("status", ""),
            )

    def _parse_message(self, msg: dict) -> dict:
        msg_type = msg.get("type", "text")
        content: dict = {"raw": msg}
        if msg_type == "text":
            content = {"body": msg.get("text", {}).get("body", "")}
        elif msg_type == "interactive":
            interactive = msg.get("interactive", {})
            content = {"interactive": interactive}
        elif msg_type in ("image", "audio", "video", "document"):
            content = {msg_type: msg.get(msg_type, {})}
        elif msg_type == "location":
            content = {"location": msg.get("location", {})}
        elif msg_type == "button":
            content = {"button": msg.get("button", {})}
        return {"type": msg_type, "content": content}
