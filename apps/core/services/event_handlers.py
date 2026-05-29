"""Registry of async event handlers."""
from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

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
    from apps.conversations.models import Conversation, Message
    from apps.conversations.services.conversation_service import ConversationService
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
            bot_reply = (result.get("message") or "").strip()
            if bot_reply:
                from apps.whatsapp.services.message_service import MessageService

                try:
                    MessageService().send_text(
                        org,
                        contact,
                        conversation,
                        bot_reply,
                        sender_type=Message.SenderType.BOT,
                    )
                except Exception:
                    logger.exception(
                        "Bot auto-reply failed for conversation %s",
                        conversation.id,
                    )
            if result.get("action") == "assign_agent":
                ConversationService().escalate_to_human(conversation)
    finally:
        set_current_organization(None)
