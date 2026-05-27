from uuid import UUID

from apps.bots.models import BotFlow, BotStep


class FlowRepository:
    def get_default_flow(self, organization_id: UUID) -> BotFlow | None:
        return (
            BotFlow.all_objects.filter(organization_id=organization_id, is_active=True)
            .order_by("-is_default", "-created_at")
            .first()
        )

    def get_step(self, flow_id: UUID, step_key: str) -> BotStep | None:
        try:
            return BotStep.all_objects.get(flow_id=flow_id, key=step_key)
        except BotStep.DoesNotExist:
            return None
