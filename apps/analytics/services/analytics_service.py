"""Analytics aggregation service."""
from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from django.db.models import Avg, Count, F, Q
from django.utils import timezone

from apps.conversations.models import Conversation, Message
from apps.payments.models import PaymentTransaction
from apps.whatsapp.models import WhatsAppMessageLog


class AnalyticsService:
    def get_dashboard_kpis(self, organization_id: UUID, days: int = 30) -> dict:
        since = timezone.now() - timedelta(days=days)
        base_conv = Conversation.all_objects.filter(
            organization_id=organization_id, created_at__gte=since
        )
        return {
            "total_conversations": base_conv.count(),
            "open_conversations": base_conv.filter(
                status__in=[Conversation.Status.OPEN, Conversation.Status.ASSIGNED]
            ).count(),
            "resolved_conversations": base_conv.filter(
                status=Conversation.Status.RESOLVED
            ).count(),
            "avg_resolution_hours": self._avg_resolution_hours(base_conv),
            "messages_sent": WhatsAppMessageLog.all_objects.filter(
                organization_id=organization_id,
                direction=WhatsAppMessageLog.Direction.OUTBOUND,
                created_at__gte=since,
            ).count(),
            "messages_received": WhatsAppMessageLog.all_objects.filter(
                organization_id=organization_id,
                direction=WhatsAppMessageLog.Direction.INBOUND,
                created_at__gte=since,
            ).count(),
            "delivery_rate": self._delivery_rate(organization_id, since),
            "payments_total": PaymentTransaction.all_objects.filter(
                organization_id=organization_id,
                status=PaymentTransaction.Status.COMPLETED,
                created_at__gte=since,
            ).aggregate(total=Count("id"), amount=Avg("amount")),
        }

    def get_agent_stats(self, organization_id: UUID, days: int = 30) -> list:
        since = timezone.now() - timedelta(days=days)
        return list(
            Conversation.all_objects.filter(
                organization_id=organization_id,
                assigned_agent__isnull=False,
                created_at__gte=since,
            )
            .values(
                agent_id=F("assigned_agent_id"),
                agent_name=F("assigned_agent__first_name"),
            )
            .annotate(
                total=Count("id"),
                resolved=Count("id", filter=Q(status=Conversation.Status.RESOLVED)),
            )
            .order_by("-total")
        )

    def export_conversations_csv(self, organization_id: UUID) -> str:
        import csv
        import io

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["id", "contact", "status", "agent", "created_at", "resolved_at"]
        )
        for conv in Conversation.all_objects.filter(
            organization_id=organization_id
        ).select_related("contact", "assigned_agent")[:10000]:
            writer.writerow(
                [
                    str(conv.id),
                    conv.contact.phone_number,
                    conv.status,
                    conv.assigned_agent.email if conv.assigned_agent else "",
                    conv.created_at.isoformat(),
                    conv.resolved_at.isoformat() if conv.resolved_at else "",
                ]
            )
        return buffer.getvalue()

    @staticmethod
    def _avg_resolution_hours(queryset) -> float:
        resolved = queryset.filter(
            resolved_at__isnull=False
        ).values_list("created_at", "resolved_at")[:1000]
        if not resolved:
            return 0.0
        total_hours = sum(
            (r[1] - r[0]).total_seconds() / 3600 for r in resolved
        )
        return round(total_hours / len(resolved), 2)

    @staticmethod
    def _delivery_rate(organization_id: UUID, since) -> float:
        outbound = WhatsAppMessageLog.all_objects.filter(
            organization_id=organization_id,
            direction=WhatsAppMessageLog.Direction.OUTBOUND,
            created_at__gte=since,
        )
        total = outbound.count()
        if not total:
            return 0.0
        delivered = outbound.filter(
            status__in=[
                WhatsAppMessageLog.Status.DELIVERED,
                WhatsAppMessageLog.Status.READ,
            ]
        ).count()
        return round(delivered / total * 100, 2)
