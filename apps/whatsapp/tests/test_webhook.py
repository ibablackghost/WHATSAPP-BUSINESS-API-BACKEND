import hashlib
import hmac
import json

import pytest
from django.conf import settings
from django.test import override_settings


@pytest.mark.django_db
class TestWhatsAppWebhook:
    def test_webhook_verification(self, api_client):
        response = api_client.get(
            "/api/v1/whatsapp/webhook/",
            {
                "hub.mode": "subscribe",
                "hub.verify_token": settings.WHATSAPP_VERIFY_TOKEN,
                "hub.challenge": "test_challenge",
            },
        )
        assert response.status_code == 200
        assert response.content == b"test_challenge"

    @override_settings(WHATSAPP_APP_SECRET="test_secret", DEBUG=False)
    def test_webhook_signature_validation(self, api_client, organization):
        organization.whatsapp_phone_number_id = "123456"
        organization.save()
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {"phone_number_id": "123456"},
                                "messages": [
                                    {
                                        "from": "221771234567",
                                        "id": "wamid.test",
                                        "type": "text",
                                        "text": {"body": "Hello"},
                                    }
                                ],
                                "contacts": [
                                    {"wa_id": "221771234567", "profile": {"name": "Test"}}
                                ],
                            }
                        }
                    ]
                }
            ]
        }
        body = json.dumps(payload).encode()
        sig = hmac.new(b"test_secret", body, hashlib.sha256).hexdigest()
        response = api_client.post(
            "/api/v1/whatsapp/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256=f"sha256={sig}",
        )
        assert response.status_code == 200

    def test_invalid_signature_rejected(self, api_client):
        response = api_client.post(
            "/api/v1/whatsapp/webhook/",
            data={"entry": []},
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256="sha256=invalid",
        )
        assert response.status_code == 403
