from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.conversations.api.serializers import ConversationSerializer, MessageSerializer
from apps.conversations.models import Conversation
from apps.conversations.services.conversation_service import ConversationService
from apps.core.api.permissions import IsOrganizationMember


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["status", "assigned_agent", "channel"]
    ordering_fields = ["last_message_at", "priority", "created_at"]

    def get_queryset(self):
        return Conversation.objects.select_related(
            "contact", "assigned_agent"
        ).prefetch_related("messages")

    @action(detail=True, methods=["post"])
    def escalate(self, request, pk=None):
        conversation = self.get_object()
        ConversationService().escalate_to_human(conversation)
        return Response(ConversationSerializer(conversation).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        from django.utils import timezone

        conversation = self.get_object()
        conversation.status = Conversation.Status.RESOLVED
        conversation.resolved_at = timezone.now()
        conversation.save(update_fields=["status", "resolved_at", "updated_at"])
        return Response(ConversationSerializer(conversation).data)
