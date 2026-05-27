"""WebSocket consumer for real-time conversations."""
import json
from typing import Any

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    """ws/conversations/<conversation_id>/"""

    async def connect(self) -> None:
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group = f"conversation_{self.conversation_id}"
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive_json(self, content: dict[str, Any], **kwargs) -> None:
        event_type = content.get("type")
        if event_type == "typing":
            await self.channel_layer.group_send(
                self.room_group,
                {"type": "typing_event", "user_id": str(self.scope["user"].id)},
            )

    async def new_message(self, event: dict) -> None:
        await self.send_json({"type": "new_message", "message": event["message"]})

    async def assigned(self, event: dict) -> None:
        await self.send_json({"type": "assigned", "agent": event["agent"]})

    async def typing_event(self, event: dict) -> None:
        await self.send_json({"type": "typing", "user_id": event["user_id"]})

    async def payment_confirmed(self, event: dict) -> None:
        await self.send_json({"type": "payment_confirmed", "payment": event["payment"]})
