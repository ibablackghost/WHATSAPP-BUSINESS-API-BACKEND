"""Meta webhook signature validation."""
from __future__ import annotations

import hashlib
import hmac

from django.conf import settings


class SignatureValidator:
    """Validates X-Hub-Signature-256 from Meta webhooks."""

    @staticmethod
    def validate(payload: bytes, signature_header: str | None) -> bool:
        if not settings.WHATSAPP_APP_SECRET:
            return settings.DEBUG  # Allow in dev without secret
        if not signature_header or not signature_header.startswith("sha256="):
            return False
        expected_sig = signature_header[7:]
        computed = hmac.new(
            settings.WHATSAPP_APP_SECRET.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(computed, expected_sig)
