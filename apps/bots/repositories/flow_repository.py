from uuid import UUID

from apps.bots.models import BotFlow, BotStep


class FlowRepository:
    def get_default_flow(self, organization_id: UUID) -> BotFlow | None:
        base = BotFlow.all_objects.filter(organization_id=organization_id, is_active=True)
        preferred = base.filter(is_default=True, steps__isnull=False).distinct()
        flow = preferred.order_by("-created_at").first()
        if flow:
            return flow
        return (
            base.filter(steps__isnull=False)
            .distinct()
            .order_by("-created_at")
            .first()
        )

    def get_step(self, flow_id: UUID, step_key: str) -> BotStep | None:
        try:
            return BotStep.all_objects.get(flow_id=flow_id, key=step_key)
        except BotStep.DoesNotExist:
            return None
