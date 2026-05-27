"""Retry failed WhatsApp messages with exponential backoff."""
from celery import shared_task


@shared_task(bind=True, max_retries=5)
def retry_failed_message(self, message_log_id: str) -> None:
    from apps.whatsapp.models import WhatsAppMessageLog
    from apps.whatsapp.services.message_service import MessageService

    try:
        log = WhatsAppMessageLog.all_objects.select_related(
            "organization", "contact", "conversation"
        ).get(id=message_log_id)
    except WhatsAppMessageLog.DoesNotExist:
        return

    if log.retry_count >= 5 or log.status != WhatsAppMessageLog.Status.FAILED:
        return

    service = MessageService()
    if log.message_type == WhatsAppMessageLog.MessageType.TEXT:
        body = log.content.get("body", "")
        service.send_text(
            log.organization, log.contact, log.conversation, body
        )
