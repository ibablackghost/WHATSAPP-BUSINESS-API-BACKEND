"""Round-robin agent assignment."""
from __future__ import annotations

from django.db.models import F
from django.utils import timezone

from apps.agents.models import AgentPresence
from apps.conversations.models import Conversation
from apps.conversations.services.websocket_service import WebSocketService


class AssignmentService:
    def assign_round_robin(self, conversation: Conversation) -> Conversation | None:
        agent_presence = (
            AgentPresence.all_objects.filter(
                organization=conversation.organization,
                status=AgentPresence.Status.ONLINE,
                active_conversations__lt=F("max_conversations"),
            )
            .order_by("active_conversations", "last_seen_at")
            .select_related("agent")
            .first()
        )
        if not agent_presence:
            conversation.status = Conversation.Status.WAITING
            conversation.save(update_fields=["status", "updated_at"])
            return conversation

        conversation.assigned_agent = agent_presence.agent
        conversation.status = Conversation.Status.ASSIGNED
        conversation.save(
            update_fields=["assigned_agent", "status", "updated_at"]
        )
        agent_presence.active_conversations = F("active_conversations") + 1
        agent_presence.save(update_fields=["active_conversations"])
        agent_presence.refresh_from_db()

        WebSocketService.broadcast_conversation(
            str(conversation.id),
            "assigned",
            {
                "agent": {
                    "id": str(agent_presence.agent_id),
                    "name": agent_presence.agent.get_full_name(),
                }
            },
        )
        return conversation

    def release_agent(self, conversation: Conversation) -> None:
        if not conversation.assigned_agent_id:
            return
        AgentPresence.all_objects.filter(
            organization=conversation.organization,
            agent_id=conversation.assigned_agent_id,
        ).update(active_conversations=F("active_conversations") - 1)
        conversation.assigned_agent = None
        conversation.save(update_fields=["assigned_agent", "updated_at"])
