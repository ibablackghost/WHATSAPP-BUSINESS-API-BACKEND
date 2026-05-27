from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api.permissions import IsOrganizationMember, IsSupervisorOrAdmin
from apps.notifications.api.serializers import NotificationCampaignSerializer
from apps.notifications.models import NotificationCampaign
from apps.notifications.services.campaign_service import CampaignService


class NotificationCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationCampaignSerializer
    permission_classes = [IsOrganizationMember, IsSupervisorOrAdmin]

    def get_queryset(self):
        return NotificationCampaign.objects.all()

    @action(detail=True, methods=["post"])
    def launch(self, request, pk=None):
        campaign = self.get_object()
        CampaignService().schedule(campaign)
        return Response(NotificationCampaignSerializer(campaign).data)
