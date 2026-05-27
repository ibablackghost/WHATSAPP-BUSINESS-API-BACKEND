"""WhatsApp message orchestration service."""
from __future__ import annotations

import logging
from typing import Any

from apps.contacts.models import Contact
from apps.conversations.models import Conversation
from apps.organizations.models import Organization
from apps.organizations.services.organization_service import OrganizationService
from apps.whatsapp.models import WhatsAppMessageLog
from apps.whatsapp.services.whatsapp_client import WhatsAppClient

logger = logging.getLogger(__name__)


class MessageService:
    def __init__(self) -> None:
        self._org_service = OrganizationService()

    def _get_client(self, organization: Organization) -> WhatsAppClient:
        token = self._org_service.get_access_token(organization)
        return WhatsAppClient(token, organization.whatsapp_phone_number_id)

    def record_inbound(
        self,
        *,
        organization: Organization,
        contact: Contact,
        conversation: Conversation,
        wa_message_id: str,
        message_type: str,
        content: dict,
    ) -> WhatsAppMessageLog:
        return WhatsAppMessageLog.all_objects.create(
            organization=organization,
            contact=contact,
            conversation=conversation,
            wa_message_id=wa_message_id,
            direction=WhatsAppMessageLog.Direction.INBOUND,
            message_type=message_type,
            content=content,
            status=WhatsAppMessageLog.Status.DELIVERED,
        )

    def send_text(
        self,
        organization: Organization,
        contact: Contact,
        conversation: Conversation,
        body: str,
    ) -> WhatsAppMessageLog:
        client = self._get_client(organization)
        log = WhatsAppMessageLog.all_objects.create(
            organization=organization,
            contact=contact,
            conversation=conversation,
            direction=WhatsAppMessageLog.Direction.OUTBOUND,
            message_type=WhatsAppMessageLog.MessageType.TEXT,
            content={"body": body},
            status=WhatsAppMessageLog.Status.PENDING,
        )
        try:
            result = client.send_text(contact.wa_id, body)
            log.wa_message_id = result.get("messages", [{}])[0].get("id", "")
            log.status = WhatsAppMessageLog.Status.SENT
            log.save(update_fields=["wa_message_id", "status", "updated_at"])
        except Exception as exc:
            log.status = WhatsAppMessageLog.Status.FAILED
            log.error_message = str(exc)
            log.retry_count += 1
            log.save(update_fields=["status", "error_message", "retry_count", "updated_at"])
            from apps.whatsapp.tasks.retry import retry_failed_message

            retry_failed_message.apply_async(args=[str(log.id)], countdown=60)
            raise
        return log

    def update_status(
        self, organization_id, wa_message_id: str, status: str
    ) -> None:
        status_map = {
            "sent": WhatsAppMessageLog.Status.SENT,
            "delivered": WhatsAppMessageLog.Status.DELIVERED,
            "read": WhatsAppMessageLog.Status.READ,
            "failed": WhatsAppMessageLog.Status.FAILED,
        }
        WhatsAppMessageLog.all_objects.filter(
            organization_id=organization_id,
            wa_message_id=wa_message_id,
        ).update(status=status_map.get(status, status))
