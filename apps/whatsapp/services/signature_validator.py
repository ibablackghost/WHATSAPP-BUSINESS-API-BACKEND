"""Meta webhook signature validation."""
from __future__ import annotations

import hashlib
import hmac
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class SignatureValidator:
    """Validates X-Hub-Signature-256 from Meta webhooks."""

    @staticmethod
    def validate(payload: bytes, signature_header: str | None) -> bool:
        if getattr(settings, "WHATSAPP_WEBHOOK_SKIP_SIGNATURE", False):
            logger.warning("Webhook signature validation disabled (dev only)")
            return True

        if not settings.WHATSAPP_APP_SECRET:
            if settings.DEBUG:
                logger.warning(
                    "WHATSAPP_APP_SECRET empty — webhook accepted in DEBUG only"
                )
                return True
            logger.error("WHATSAPP_APP_SECRET missing in production")
            return False

        if not signature_header:
            logger.warning("Webhook POST without X-Hub-Signature-256 header")
            return False

        if not signature_header.startswith("sha256="):
            logger.warning("Invalid X-Hub-Signature-256 format")
            return False

        expected_sig = signature_header[7:]
        computed = hmac.new(
            settings.WHATSAPP_APP_SECRET.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(computed, expected_sig):
            logger.warning(
                "Webhook signature mismatch — update WHATSAPP_APP_SECRET in .env "
                "(Meta Developer → Paramètres → Secret d'application) "
                "or set WHATSAPP_WEBHOOK_SKIP_SIGNATURE=true for local dev"
            )
            return False
        return True
