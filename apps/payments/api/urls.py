from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.payments.api.views import (
    PaymentInitiateView,
    PaymentTransactionViewSet,
    WaveWebhookView,
)

router = DefaultRouter()
router.register("transactions", PaymentTransactionViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
    path("initiate/", PaymentInitiateView.as_view(), name="payment-initiate"),
    path("webhooks/wave/", WaveWebhookView.as_view(), name="wave-webhook"),
]
