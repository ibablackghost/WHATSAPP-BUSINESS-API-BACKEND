"""Broadcast events to WebSocket groups."""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class WebSocketService:
    @staticmethod
    def broadcast_conversation(conversation_id: str, event_type: str, data: dict) -> None:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"conversation_{conversation_id}",
            {"type": event_type, **data},
        )
