"""Validate Meta WhatsApp credentials against Graph API."""
from __future__ import annotations

from typing import Any

import httpx
from django.conf import settings

from apps.whatsapp.services.whatsapp_errors import log_graph_error, parse_graph_error


class WhatsAppCredentialValidator:
    """Verify access token + phone number ID with a lightweight Graph API call."""

    def validate(self, access_token: str, phone_number_id: str) -> dict[str, Any]:
        token = (access_token or "").strip()
        phone_id = (phone_number_id or "").strip()
        if not token:
            return {
                "valid": False,
                "error": "access_token manquant",
                "hint": "POST /api/v1/organizations/whatsapp-config/",
            }
        if not phone_id:
            return {
                "valid": False,
                "error": "phone_number_id manquant",
                "hint": "POST /api/v1/organizations/whatsapp-config/",
            }

        url = f"{settings.WHATSAPP_GRAPH_URL}/{phone_id}"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                url,
                params={"fields": "verified_name,display_phone_number,quality_rating"},
                headers={"Authorization": f"Bearer {token}"},
            )

        if response.is_success:
            data = response.json()
            return {
                "valid": True,
                "phone_number_id": phone_id,
                "verified_name": data.get("verified_name"),
                "display_phone_number": data.get("display_phone_number"),
            }

        log_graph_error(response, context="validate credentials")
        details = parse_graph_error(response)
        return {
            "valid": False,
            "phone_number_id": phone_id,
            "error": details.get("message") or "Meta Graph API rejected credentials",
            "code": details.get("code"),
            "hint": (
                "Regénérez le token dans Meta Developer (nouvelle app) puis "
                "POST /api/v1/organizations/whatsapp-config/"
            ),
            "details": details,
        }
