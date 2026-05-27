from django.urls import path

from apps.whatsapp.api.views import SendMessageView, WhatsAppWebhookView

urlpatterns = [
    path("webhook/", WhatsAppWebhookView.as_view(), name="whatsapp-webhook"),
    path("send/", SendMessageView.as_view(), name="whatsapp-send"),
]
