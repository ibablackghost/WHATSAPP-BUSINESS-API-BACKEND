"""WhatsApp message orchestration service."""
from __future__ import annotations

import logging

import httpx

from apps.contacts.models import Contact
from apps.conversations.models import Conversation, Message
from apps.conversations.services.conversation_service import ConversationService
from apps.organizations.models import Organization
from apps.organizations.services.organization_service import OrganizationService
from apps.whatsapp.exceptions import WhatsAppNotConfiguredError
from apps.whatsapp.models import WhatsAppMessageLog
from apps.whatsapp.services.whatsapp_client import WhatsAppClient
from apps.whatsapp.services.whatsapp_errors import is_retryable_status

logger = logging.getLogger(__name__)


class MessageService:
    def __init__(self) -> None:
        self._org_service = OrganizationService()
        self._conversation_service = ConversationService()

    def _display_text(self, message_type: str, content: dict) -> str:
        if message_type == "text":
            return content.get("body", "")
        if message_type == "button":
            return content.get("button", {}).get("text", "[Bouton]")
        if message_type == "interactive":
            interactive = content.get("interactive", {})
            reply = interactive.get("button_reply") or interactive.get("list_reply")
            if reply:
                return reply.get("title", reply.get("id", "[Réponse interactive]"))
        return f"[{message_type}]"

    def _persist_chat_message(
        self,
        conversation: Conversation,
        *,
        sender_type: str,
        content: str,
        sender_id: str = "",
        content_type: str = "text",
    ) -> Message:
        msg = self._conversation_service.add_message(
            conversation,
            sender_type=sender_type,
            content=content,
            sender_id=sender_id,
            content_type=content_type,
        )
        self._broadcast_new_message(str(conversation.id), msg)
        return msg

    def _broadcast_new_message(self, conversation_id: str, message: Message) -> None:
        from apps.conversations.api.serializers import MessageSerializer
        from apps.conversations.services.websocket_service import WebSocketService

        WebSocketService.broadcast_conversation(
            conversation_id,
            "new_message",
            {"message": MessageSerializer(message).data},
        )

    def _get_client(self, organization: Organization) -> WhatsAppClient:
        if not organization.whatsapp_phone_number_id:
            raise WhatsAppNotConfiguredError(
                "phone_number_id manquant. "
                "POST /api/v1/organizations/whatsapp-config/"
            )
        token = self._org_service.get_access_token(organization)
        if not token:
            raise WhatsAppNotConfiguredError(
                "Token Meta manquant ou illisible. "
                "Refaire POST /api/v1/organizations/whatsapp-config/ "
                "avec un access_token de la nouvelle app Meta."
            )
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
        log = WhatsAppMessageLog.all_objects.create(
            organization=organization,
            contact=contact,
            conversation=conversation,
            wa_message_id=wa_message_id,
            direction=WhatsAppMessageLog.Direction.INBOUND,
            message_type=message_type,
            content=content,
            status=WhatsAppMessageLog.Status.DELIVERED,
        )
        body = self._display_text(message_type, content)
        if body:
            self._persist_chat_message(
                conversation,
                sender_type=Message.SenderType.CONTACT,
                content=body,
                sender_id=contact.wa_id,
                content_type=message_type,
            )
        return log

    def send_text(
        self,
        organization: Organization,
        contact: Contact,
        conversation: Conversation,
        body: str,
        *,
        sender_type: str = Message.SenderType.AGENT,
        sender_id: str = "",
    ) -> WhatsAppMessageLog:
        body = (body or "").strip()
        if not body:
            raise ValueError("Message body cannot be empty")

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
            self._persist_chat_message(
                conversation,
                sender_type=sender_type,
                content=body,
                sender_id=sender_id,
            )
        except httpx.HTTPStatusError as exc:
            log.status = WhatsAppMessageLog.Status.FAILED
            log.error_message = exc.response.text[:1000]
            log.retry_count += 1
            log.save(update_fields=["status", "error_message", "retry_count", "updated_at"])
            if is_retryable_status(exc.response.status_code):
                from apps.whatsapp.tasks.retry import retry_failed_message

                retry_failed_message.apply_async(args=[str(log.id)], countdown=60)
            raise
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
