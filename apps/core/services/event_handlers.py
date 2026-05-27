"""Registry of async event handlers."""
from __future__ import annotations

from typing import Any, Callable

EVENT_HANDLERS: dict[str, Callable[..., None]] = {}


def register_handler(event_type: str):
    """Decorator to register Celery event handlers."""

    def decorator(fn: Callable[..., None]) -> Callable[..., None]:
        EVENT_HANDLERS[event_type] = fn
        return fn

    return decorator


@register_handler("whatsapp.message.received")
def handle_incoming_whatsapp(organization_id: str | None, payload: dict[str, Any]) -> None:
    """Route inbound WhatsApp messages to flow engine or live chat."""
    from apps.bots.services.flow_engine import FlowEngine
    from apps.contacts.models import Contact
    from apps.conversations.models import Conversation
    from apps.conversations.services.conversation_service import ConversationService
    from apps.conversations.services.websocket_service import WebSocketService
    from apps.core.middleware.organization import set_current_organization
    from apps.organizations.models import Organization

    if not organization_id:
        return

    org = Organization.objects.get(id=organization_id)
    set_current_organization(org)
    try:
        contact = Contact.all_objects.get(id=payload["contact_id"])
        conversation = Conversation.all_objects.get(id=payload["conversation_id"])
        message = payload.get("message", {})
        user_input = message.get("content", {}).get("body", "")

        if conversation.is_bot_active:
            result = FlowEngine().start_or_resume(org, contact, conversation, user_input)
            if result.get("message"):
                from apps.whatsapp.services.message_service import MessageService

                MessageService().send_text(org, contact, conversation, result["message"])
            if result.get("action") == "assign_agent":
                ConversationService().escalate_to_human(conversation)
        else:
            ConversationService().add_message(
                conversation,
                sender_type="contact",
                content=user_input,
                sender_id=contact.wa_id,
            )
            WebSocketService.broadcast_conversation(
                str(conversation.id),
                "new_message",
                {"message": {"content": user_input, "sender_type": "contact"}},
            )
    finally:
        set_current_organization(None)
