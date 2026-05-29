from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api.permissions import IsAdmin, IsOrganizationMember
from apps.organizations.api.serializers import OrganizationSerializer
from apps.organizations.api.serializers_whatsapp import WhatsAppConfigSerializer
from apps.organizations.services.organization_service import OrganizationService
from apps.whatsapp.services.credential_validator import WhatsAppCredentialValidator


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
        data = serializer.validated_data

        validation = WhatsAppCredentialValidator().validate(
            data["access_token"],
            data["phone_number_id"],
        )
        if not validation.get("valid"):
            return Response(
                {
                    "detail": validation.get("error", "Credentials Meta invalides"),
                    "code": validation.get("code"),
                    "hint": validation.get("hint"),
                    "details": validation.get("details"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = OrganizationService()
        service.set_whatsapp_credentials(
            request.organization,
            phone_number_id=data["phone_number_id"],
            business_account_id=data["business_account_id"],
            access_token=data["access_token"],
        )
        return Response(
            {
                "status": "configured",
                "phone_number_id": data["phone_number_id"],
                "verified_name": validation.get("verified_name"),
                "display_phone_number": validation.get("display_phone_number"),
            },
            status=status.HTTP_200_OK,
        )


class OrganizationWhatsAppStatusView(APIView):
    """Vérifie les credentials WhatsApp stockés pour l'organisation."""

    permission_classes = [IsOrganizationMember, IsAdmin]

    def get(self, request):
        org = request.organization
        service = OrganizationService()
        token = service.get_access_token(org)
        validation = WhatsAppCredentialValidator().validate(
            token, org.whatsapp_phone_number_id
        )
        return Response(
            {
                "organization_id": str(org.id),
                "phone_number_id": org.whatsapp_phone_number_id or None,
                "has_access_token": bool(token),
                **validation,
            }
        )


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
