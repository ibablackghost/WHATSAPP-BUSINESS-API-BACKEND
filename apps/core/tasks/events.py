"""Celery task for async event dispatch."""
from celery import shared_task


@shared_task(bind=True, max_retries=3)
def dispatch_event(
    self,
    event_type: str,
    organization_id: str | None,
    payload: dict,
) -> None:
    """Route domain events to registered Celery handlers."""
    from apps.core.services.event_handlers import EVENT_HANDLERS

    handler = EVENT_HANDLERS.get(event_type)
    if handler:
        handler(organization_id=organization_id, payload=payload)
