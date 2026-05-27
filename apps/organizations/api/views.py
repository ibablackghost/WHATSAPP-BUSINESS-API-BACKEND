from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api.permissions import IsAdmin, IsOrganizationMember
from apps.organizations.api.serializers import OrganizationSerializer
from apps.organizations.api.serializers_whatsapp import WhatsAppConfigSerializer
from apps.organizations.services.organization_service import OrganizationService


class CurrentOrganizationView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        return Response(OrganizationSerializer(request.organization).data)


class OrganizationWhatsAppConfigView(APIView):
    permission_classes = [IsOrganizationMember, IsAdmin]

    @extend_schema(
        request=WhatsAppConfigSerializer,
        responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}},
        parameters=[
            OpenApiParameter(
                name="X-Organization-ID",
                type=str,
                location=OpenApiParameter.HEADER,
                required=False,
                description="UUID organisation (optionnel si une seule org par défaut)",
            )
        ],
        description=(
            "Enregistre les credentials WhatsApp Cloud API pour l'organisation courante. "
            "Authentification JWT obligatoire (Authorize dans Swagger)."
        ),
    )
    def post(self, request):
        serializer = WhatsAppConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = OrganizationService()
        service.set_whatsapp_credentials(
            request.organization,
            phone_number_id=serializer.validated_data["phone_number_id"],
            business_account_id=serializer.validated_data["business_account_id"],
            access_token=serializer.validated_data["access_token"],
        )
        return Response({"status": "configured"}, status=status.HTTP_200_OK)


class OrganizationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        org_ids = self.request.user.memberships.filter(is_active=True).values_list(
            "organization_id", flat=True
        )
        from apps.organizations.models import Organization

        return Organization.objects.filter(id__in=org_ids)

    def perform_create(self, serializer):
        service = OrganizationService()
        org = service.create_organization(
            name=serializer.validated_data["name"],
            slug=serializer.validated_data["slug"],
            owner=self.request.user,
            plan=serializer.validated_data.get("plan", "free"),
        )
        serializer.instance = org
