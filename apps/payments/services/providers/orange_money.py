import httpx
from django.conf import settings

from apps.payments.services.providers.base import BasePaymentProvider, PaymentResult


class OrangeMoneyProvider(BasePaymentProvider):
    """Orange Money API integration (West Africa)."""

    def initiate(
        self, amount: float, currency: str, phone: str, description: str
    ) -> PaymentResult:
        with httpx.Client(timeout=30.0) as client:
            token_resp = client.post(
                "https://api.orange.com/oauth/v3/token",
                data={"grant_type": "client_credentials"},
                auth=(settings.ORANGE_MONEY_CLIENT_ID, settings.ORANGE_MONEY_CLIENT_SECRET),
            )
            token_resp.raise_for_status()
            token = token_resp.json()["access_token"]
            response = client.post(
                "https://api.orange.com/orange-money-webpay/dev/v1/webpayment",
                json={
                    "merchant_key": settings.ORANGE_MONEY_CLIENT_ID,
                    "currency": currency,
                    "order_id": description,
                    "amount": amount,
                    "return_url": "https://whatbot.pro/payment/callback",
                    "cancel_url": "https://whatbot.pro/payment/cancel",
                    "notif_url": "https://whatbot.pro/api/v1/payments/webhooks/orange/",
                    "lang": "fr",
                    "reference": phone,
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()
            return PaymentResult(
                external_id=data.get("pay_token", ""),
                payment_url=data.get("payment_url", ""),
                status="pending",
                raw_response=data,
            )

    def verify_webhook(self, payload: dict, signature: str) -> bool:
        return bool(payload.get("status"))

    def get_status(self, external_id: str) -> str:
        return "pending"
