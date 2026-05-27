from __future__ import annotations

from django.utils import timezone

from apps.contacts.models import Contact
from apps.conversations.models import Conversation, Message
from apps.organizations.models import Organization


class ConversationService:
    def get_or_create_for_contact(
        self, organization: Organization, contact: Contact
    ) -> Conversation:
        existing = Conversation.all_objects.filter(
            organization=organization,
            contact=contact,
            status__in=[
                Conversation.Status.OPEN,
                Conversation.Status.ASSIGNED,
                Conversation.Status.WAITING,
            ],
        ).first()
        if existing:
            return existing
        return Conversation.all_objects.create(
            organization=organization,
            contact=contact,
            status=Conversation.Status.OPEN,
            channel=Conversation.Channel.WHATSAPP,
        )

    def add_message(
        self,
        conversation: Conversation,
        *,
        sender_type: str,
        content: str,
        sender_id: str = "",
        content_type: str = "text",
    ) -> Message:
        msg = Message.all_objects.create(
            organization=conversation.organization,
            conversation=conversation,
            sender_type=sender_type,
            sender_id=sender_id,
            content=content,
            content_type=content_type,
        )
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=["last_message_at", "updated_at"])
        return msg

    def escalate_to_human(self, conversation: Conversation) -> Conversation:
        conversation.is_bot_active = False
        conversation.status = Conversation.Status.WAITING
        conversation.save(update_fields=["is_bot_active", "status", "updated_at"])
        from apps.agents.services.assignment_service import AssignmentService

        AssignmentService().assign_round_robin(conversation)
        return conversation
