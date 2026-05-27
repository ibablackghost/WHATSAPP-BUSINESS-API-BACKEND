"""Root WebSocket hub — point d'entrée /ws pour le frontend."""
from __future__ import annotations

from typing import Any

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class RootWebSocketConsumer(AsyncJsonWebsocketConsumer):
    """
    Hub WebSocket principal.

    URL: ws://127.0.0.1:8000/ws?token=<JWT_ACCESS_TOKEN>

    Routes dédiées (recommandées en production) :
    - ws/conversations/<uuid>/
    - ws/agents/
    - ws/notifications/
    """

    async def connect(self) -> None:
        user = self.scope.get("user")
        await self.accept()
        if user and user.is_authenticated:
            self.user_group = f"user_{user.id}"
            await self.channel_layer.group_add(self.user_group, self.channel_name)
            await self.send_json(
                {
                    "type": "connected",
                    "user_id": str(user.id),
                    "routes": {
                        "conversations": "ws/conversations/<conversation_id>/",
                        "agents": "ws/agents/",
                        "notifications": "ws/notifications/",
                    },
                }
            )
        else:
            await self.send_json(
                {
                    "type": "auth_required",
                    "message": "Ajoutez ?token=<JWT_ACCESS_TOKEN> à l'URL WebSocket.",
                    "example": "ws://127.0.0.1:8000/ws?token=eyJ...",
                    "routes": {
                        "conversations": "ws/conversations/<conversation_id>/",
                        "agents": "ws/agents/",
                        "notifications": "ws/notifications/",
                    },
                }
            )

    async def disconnect(self, close_code: int) -> None:
        if hasattr(self, "user_group"):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive_json(self, content: dict[str, Any], **kwargs) -> None:
        if content.get("type") == "ping":
            await self.send_json({"type": "pong"})

    async def notify(self, event: dict) -> None:
        await self.send_json({"type": "notification", "payload": event.get("payload", {})})
