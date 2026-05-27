"""Event-driven architecture — domain events dispatcher."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

EventHandler = Callable[["DomainEvent"], None]


@dataclass(frozen=True)
class DomainEvent:
    """Base domain event."""

    event_id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    organization_id: UUID | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventBus:
    """Simple in-process event bus. Celery tasks subscribe for async processing."""

    _handlers: dict[str, list[EventHandler]] = {}

    @classmethod
    def subscribe(cls, event_type: str, handler: EventHandler) -> None:
        cls._handlers.setdefault(event_type, []).append(handler)

    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        logger.info("Event published: %s", event.event_type)
        for handler in cls._handlers.get(event.event_type, []):
            try:
                handler(event)
            except Exception:
                logger.exception("Handler failed for %s", event.event_type)

        # Async fan-out via Celery
        from apps.core.tasks.events import dispatch_event

        dispatch_event.delay(
            event_type=event.event_type,
            organization_id=str(event.organization_id) if event.organization_id else None,
            payload=event.payload,
        )


event_bus = EventBus()
