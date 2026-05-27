import hashlib
import hmac

import httpx
from django.conf import settings

from apps.payments.services.providers.base import BasePaymentProvider, PaymentResult


class WaveProvider(BasePaymentProvider):
    BASE_URL = "https://api.wave.com/v1"

    def initiate(
        self, amount: float, currency: str, phone: str, description: str
    ) -> PaymentResult:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.BASE_URL}/checkout/sessions",
                json={
                    "amount": str(amount),
                    "currency": currency,
                    "client_reference": description,
                    "success_url": "https://whatbot.pro/payment/success",
                    "error_url": "https://whatbot.pro/payment/error",
                },
                headers={"Authorization": f"Bearer {settings.WAVE_API_KEY}"},
            )
            response.raise_for_status()
            data = response.json()
            return PaymentResult(
                external_id=data.get("id", ""),
                payment_url=data.get("wave_launch_url", ""),
                status="pending",
                raw_response=data,
            )

    def verify_webhook(self, payload: dict, signature: str) -> bool:
        secret = settings.WAVE_WEBHOOK_SECRET.encode()
        computed = hmac.new(secret, str(payload).encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, signature)

    def get_status(self, external_id: str) -> str:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{self.BASE_URL}/checkout/sessions/{external_id}",
                headers={"Authorization": f"Bearer {settings.WAVE_API_KEY}"},
            )
            response.raise_for_status()
            return response.json().get("payment_status", "pending")
