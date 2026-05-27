from celery import shared_task


@shared_task(bind=True, max_retries=5)
def retry_pending_payment(self, transaction_id: str) -> None:
    from apps.payments.models import PaymentTransaction
    from apps.payments.services.payment_service import PaymentService

    try:
        tx = PaymentTransaction.all_objects.get(id=transaction_id)
    except PaymentTransaction.DoesNotExist:
        return
    if tx.status != PaymentTransaction.Status.PENDING or tx.retry_count >= 5:
        return
    service = PaymentService()
    provider_cls = service.PROVIDERS.get(tx.provider)
    if provider_cls:
        status = provider_cls().get_status(tx.external_id)
        if status in ("completed", "success"):
            service.confirm_payment(tx)
        else:
            tx.retry_count += 1
            tx.save(update_fields=["retry_count", "updated_at"])
            raise self.retry(countdown=60 * tx.retry_count)
