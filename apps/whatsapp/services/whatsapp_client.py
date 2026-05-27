"""WhatsApp Cloud API HTTP client with exponential backoff."""
from __future__ import annotations

import logging
from typing import Any

import httpx
from django.conf import settings
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """Low-level client for Meta Graph API WhatsApp endpoints."""

    def __init__(self, access_token: str, phone_number_id: str) -> None:
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = settings.WHATSAPP_GRAPH_URL
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @property
    def messages_url(self) -> str:
        return f"{self.base_url}/{self.phone_number_id}/messages"

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        reraise=True,
    )
    def send_message(self, payload: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                self.messages_url,
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    def send_text(self, to: str, body: str, preview_url: bool = False) -> dict[str, Any]:
        return self.send_message(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {"preview_url": preview_url, "body": body},
            }
        )

    def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str,
        components: list | None = None,
    ) -> dict[str, Any]:
        template: dict[str, Any] = {
            "name": template_name,
            "language": {"code": language_code},
        }
        if components:
            template["components"] = components
        return self.send_message(
            {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": template,
            }
        )

    def send_interactive_buttons(
        self, to: str, body: str, buttons: list[dict[str, str]]
    ) -> dict[str, Any]:
        return self.send_message(
            {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": body},
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {"id": b["id"], "title": b["title"][:20]},
                            }
                            for b in buttons[:3]
                        ]
                    },
                },
            }
        )

    def send_interactive_list(
        self,
        to: str,
        body: str,
        button_text: str,
        sections: list[dict],
    ) -> dict[str, Any]:
        return self.send_message(
            {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {"text": body},
                    "action": {"button": button_text, "sections": sections},
                },
            }
        )

    def send_media(
        self, to: str, media_type: str, media_id: str, caption: str = ""
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": media_type,
            media_type: {"id": media_id},
        }
        if caption and media_type in ("image", "video", "document"):
            payload[media_type]["caption"] = caption
        return self.send_message(payload)

    def send_location(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: str = "",
        address: str = "",
    ) -> dict[str, Any]:
        return self.send_message(
            {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "location",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "name": name,
                    "address": address,
                },
            }
        )
