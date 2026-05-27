"""Payment orchestration service."""
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.utils import timezone

from apps.contacts.models import Contact
from apps.conversations.services.websocket_service import WebSocketService
from apps.payments.models import PaymentTransaction
from apps.payments.services.providers.free_money import FreeMoneyProvider
from apps.payments.services.providers.orange_money import OrangeMoneyProvider
from apps.payments.services.providers.wave import WaveProvider

if TYPE_CHECKING:
    from apps.bots.models import SessionState


class PaymentService:
    PROVIDERS = {
        PaymentTransaction.Provider.WAVE: WaveProvider,
        PaymentTransaction.Provider.ORANGE_MONEY: OrangeMoneyProvider,
        PaymentTransaction.Provider.FREE_MONEY: FreeMoneyProvider,
    }

    def initiate(
        self,
        *,
        organization,
        contact: Contact,
        provider: str,
        amount: Decimal,
        phone_number: str,
        description: str = "",
        conversation=None,
    ) -> PaymentTransaction:
        provider_cls = self.PROVIDERS.get(provider)
        if not provider_cls:
            raise ValueError(f"Unknown provider: {provider}")

        result = provider_cls().initiate(
            float(amount), "XOF", phone_number, description
        )
        return PaymentTransaction.all_objects.create(
            organization=organization,
            contact=contact,
            conversation=conversation,
            provider=provider,
            amount=amount,
            phone_number=phone_number,
            description=description,
            external_id=result.external_id,
            payment_url=result.payment_url,
            metadata=result.raw_response,
        )

    def initiate_from_flow(self, session: SessionState, config: dict) -> PaymentTransaction:
        return self.initiate(
            organization=session.organization,
            contact=session.contact,
            provider=config.get("provider", "wave"),
            amount=Decimal(str(config.get("amount", 0))),
            phone_number=session.contact.phone_number,
            description=config.get("description", ""),
            conversation=session.conversation,
        )

    def confirm_payment(self, transaction: PaymentTransaction) -> PaymentTransaction:
        transaction.status = PaymentTransaction.Status.COMPLETED
        transaction.completed_at = timezone.now()
        transaction.save(update_fields=["status", "completed_at", "updated_at"])
        if transaction.conversation_id:
            WebSocketService.broadcast_conversation(
                str(transaction.conversation_id),
                "payment_confirmed",
                {
                    "payment": {
                        "id": str(transaction.id),
                        "amount": str(transaction.amount),
                        "provider": transaction.provider,
                    }
                },
            )
        return transaction

    def handle_webhook(
        self, provider: str, payload: dict, signature: str = ""
    ) -> PaymentTransaction | None:
        provider_cls = self.PROVIDERS.get(provider)
        if not provider_cls or not provider_cls().verify_webhook(payload, signature):
            return None
        external_id = payload.get("id") or payload.get("transaction_id", "")
        try:
            transaction = PaymentTransaction.all_objects.get(
                external_id=external_id, provider=provider
            )
        except PaymentTransaction.DoesNotExist:
            return None
        status = payload.get("status", "completed")
        if status in ("completed", "success", "SUCCESS"):
            return self.confirm_payment(transaction)
        transaction.status = PaymentTransaction.Status.FAILED
        transaction.save(update_fields=["status", "updated_at"])
        return transaction
