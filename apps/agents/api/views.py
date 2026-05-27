from rest_framework import viewsets

from apps.agents.api.serializers import AgentPresenceSerializer
from apps.agents.models import AgentPresence
from apps.core.api.permissions import IsOrganizationMember


class AgentPresenceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AgentPresenceSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        return AgentPresence.objects.select_related("agent")
