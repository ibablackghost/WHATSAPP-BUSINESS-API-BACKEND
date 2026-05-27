from channels.generic.websocket import AsyncJsonWebsocketConsumer


class AgentConsumer(AsyncJsonWebsocketConsumer):
    """ws/agents/ — agent presence and status."""

    async def connect(self) -> None:
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return
        self.room_group = f"agents_{user.id}"
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()
        await self.send_json({"type": "connected"})

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive_json(self, content, **kwargs) -> None:
        if content.get("type") == "status":
            from channels.db import database_sync_to_async
            from apps.agents.services.presence_service import PresenceService

            await database_sync_to_async(PresenceService().set_status)(
                user=self.scope["user"],
                status=content.get("status", "online"),
            )

    async def online_status(self, event) -> None:
        await self.send_json({"type": "online_status", "agents": event["agents"]})
