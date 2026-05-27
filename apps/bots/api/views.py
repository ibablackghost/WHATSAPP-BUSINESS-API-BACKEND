from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.bots.api.serializers import BotFlowSerializer, BotStepSerializer
from apps.bots.models import BotFlow, BotStep
from apps.core.api.permissions import IsOrganizationMember, IsSupervisorOrAdmin


class BotFlowViewSet(viewsets.ModelViewSet):
    serializer_class = BotFlowSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["is_active", "is_default"]
    search_fields = ["name", "slug"]

    def get_queryset(self):
        return BotFlow.objects.prefetch_related("steps")

    def get_permissions(self):
        if self.action in (
            "create",
            "update",
            "partial_update",
            "destroy",
            "sync_steps",
        ):
            return [IsOrganizationMember(), IsSupervisorOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=["put"], url_path="sync-steps")
    def sync_steps(self, request, pk=None):
        """Replace all steps for a flow (used by the visual bot builder)."""
        flow = self.get_object()
        steps_payload = request.data
        if isinstance(steps_payload, dict):
            steps_payload = steps_payload.get("steps", [])

        flow.steps.all().delete()
        created = []
        for item in steps_payload:
            serializer = BotStepSerializer(data=item)
            serializer.is_valid(raise_exception=True)
            created.append(
                BotStep.all_objects.create(
                    organization=flow.organization,
                    flow=flow,
                    **serializer.validated_data,
                )
            )

        flow.refresh_from_db()
        return Response(
            BotFlowSerializer(flow, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )
