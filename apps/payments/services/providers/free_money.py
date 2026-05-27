import httpx
from django.conf import settings

from apps.payments.services.providers.base import BasePaymentProvider, PaymentResult


class FreeMoneyProvider(BasePaymentProvider):
    """Free Money (Tigo Cash) integration."""

    def initiate(
        self, amount: float, currency: str, phone: str, description: str
    ) -> PaymentResult:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://api.free.sn/v1/payments",
                json={
                    "amount": amount,
                    "currency": currency,
                    "phone": phone,
                    "description": description,
                },
                headers={"X-API-Key": settings.FREE_MONEY_API_KEY},
            )
            response.raise_for_status()
            data = response.json()
            return PaymentResult(
                external_id=data.get("transaction_id", ""),
                payment_url=data.get("payment_link", ""),
                status="pending",
                raw_response=data,
            )

    def verify_webhook(self, payload: dict, signature: str) -> bool:
        return payload.get("api_key") == settings.FREE_MONEY_API_KEY

    def get_status(self, external_id: str) -> str:
        return "pending"
