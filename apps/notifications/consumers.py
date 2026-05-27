from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """ws/notifications/ — real-time notification events."""

    async def connect(self) -> None:
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return
        self.room_group = f"notifications_{user.id}"
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def campaign_update(self, event) -> None:
        await self.send_json({"type": "campaign_update", "campaign": event["campaign"]})
