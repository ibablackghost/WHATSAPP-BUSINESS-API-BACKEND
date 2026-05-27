from celery import shared_task


@shared_task(bind=True, max_retries=3)
def process_webhook_async(self, payload: dict) -> None:
    from apps.whatsapp.services.webhook_service import WebhookService

    WebhookService().process_payload(payload)
