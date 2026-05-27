from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api.permissions import IsOrganizationMember
from apps.payments.api.serializers import PaymentTransactionSerializer
from apps.payments.models import PaymentTransaction
from apps.payments.services.payment_service import PaymentService


class PaymentTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["status", "provider"]

    def get_queryset(self):
        return PaymentTransaction.objects.select_related("contact")


class PaymentInitiateView(APIView):
    permission_classes = [IsOrganizationMember]

    def post(self, request):
        from apps.contacts.models import Contact

        contact = Contact.objects.get(id=request.data["contact_id"])
        payment = PaymentService().initiate(
            organization=request.organization,
            contact=contact,
            provider=request.data["provider"],
            amount=request.data["amount"],
            phone_number=request.data.get("phone_number", contact.phone_number),
            description=request.data.get("description", ""),
        )
        return Response(
            PaymentTransactionSerializer(payment).data, status=status.HTTP_201_CREATED
        )


class WaveWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        signature = request.META.get("HTTP_WAVE_SIGNATURE", "")
        result = PaymentService().handle_webhook("wave", request.data, signature)
        return Response({"status": "ok" if result else "ignored"})
