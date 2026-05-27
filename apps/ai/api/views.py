from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.api.serializers import FAQEntrySerializer
from apps.ai.models import FAQEntry
from apps.ai.services.chat_service import ChatService
from apps.ai.services.rag_service import RAGService
from apps.ai.tasks.indexing import index_faq_entry
from apps.core.api.permissions import IsOrganizationMember


class FAQEntryViewSet(viewsets.ModelViewSet):
    serializer_class = FAQEntrySerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["category", "language", "is_active"]
    search_fields = ["question", "answer"]

    def get_queryset(self):
        return FAQEntry.objects.all()

    def perform_create(self, serializer):
        faq = serializer.save()
        index_faq_entry.delay(str(faq.id))


class AIChatView(APIView):
    permission_classes = [IsOrganizationMember]

    def post(self, request):
        contact_id = request.data.get("contact_id")
        message = request.data.get("message", "")
        result = ChatService().generate_response(
            organization_id=request.organization.id,
            contact_id=contact_id,
            message=message,
        )
        return Response(result)


class SemanticSearchView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        query = request.query_params.get("q", "")
        results = RAGService().search(request.organization.id, query)
        return Response(FAQEntrySerializer(results, many=True).data)
