from django.conf import settings
from django.http import HttpResponse
import httpx
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.core.api.permissions import IsOrganizationMember
from apps.whatsapp.api.serializers import SendMessageSerializer
from apps.whatsapp.exceptions import WhatsAppNotConfiguredError
from apps.whatsapp.services.message_service import MessageService
from apps.whatsapp.services.signature_validator import SignatureValidator
from apps.whatsapp.services.webhook_runner import enqueue_webhook_processing


class WebhookThrottle(AnonRateThrottle):
    scope = "webhook"


class WhatsAppWebhookView(APIView):
    """Meta WhatsApp webhook — GET verification, POST messages."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [WebhookThrottle]

    def get(self, request):
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            return HttpResponse(challenge, content_type="text/plain")
        if settings.DEBUG and not mode:
            return HttpResponse(
                "Webhook OK. Meta doit appeler avec hub.mode=subscribe et "
                f"hub.verify_token={settings.WHATSAPP_VERIFY_TOKEN!r}",
                content_type="text/plain",
                status=200,
            )
        return HttpResponse("Forbidden", status=403)

    def post(self, request):
        signature = request.META.get("HTTP_X_HUB_SIGNATURE_256")
        raw_body = getattr(request, "_request", request).body
        if not SignatureValidator.validate(raw_body, signature):
            return Response(
                {
                    "detail": (
                        "Invalid webhook signature. "
                        "Set WHATSAPP_APP_SECRET to your Meta App Secret."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        enqueue_webhook_processing(request.data)
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class SendMessageView(APIView):
    permission_classes = [IsOrganizationMember]

    def post(self, request):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from apps.contacts.models import Contact
        from apps.conversations.models import Conversation

        contact = Contact.objects.get(id=serializer.validated_data["contact_id"])
        conversation = Conversation.objects.get(
            id=serializer.validated_data["conversation_id"]
        )
        service = MessageService()
        try:
            log = service.send_text(
                request.organization,
                contact,
                conversation,
                serializer.validated_data["body"],
                sender_id=str(request.user.id),
            )
        except WhatsAppNotConfiguredError as exc:
            return Response(
                {"detail": str(exc), "hint": "POST /api/v1/organizations/whatsapp-config/"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except httpx.HTTPStatusError as exc:
            upstream_detail = "Meta Graph API rejected the request"
            try:
                upstream_json = exc.response.json()
                upstream_detail = upstream_json.get("error", {}).get(
                    "message", upstream_detail
                )
            except Exception:
                pass
            return Response(
                {
                    "detail": upstream_detail,
                    "upstream_status": exc.response.status_code,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({"message_id": str(log.id), "wa_message_id": log.wa_message_id})
