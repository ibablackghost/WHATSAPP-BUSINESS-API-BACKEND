"""Enqueue webhook processing without blocking the HTTP response to Meta."""
from __future__ import annotations

import logging
from threading import Thread
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


def _process_payload(payload: dict[str, Any]) -> None:
    from apps.whatsapp.services.webhook_service import WebhookService

    try:
        WebhookService().process_payload(payload)
    except Exception:
        logger.exception("Webhook processing failed")


def enqueue_webhook_processing(payload: dict[str, Any]) -> None:
    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
        Thread(target=_process_payload, args=(payload,), daemon=True).start()
        return

    from apps.whatsapp.tasks.webhook import process_webhook_async

    process_webhook_async.delay(payload)
