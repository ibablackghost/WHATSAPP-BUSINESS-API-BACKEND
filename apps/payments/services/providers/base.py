from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentResult:
    external_id: str
    payment_url: str
    status: str
    raw_response: dict


class BasePaymentProvider(ABC):
    @abstractmethod
    def initiate(
        self, amount: float, currency: str, phone: str, description: str
    ) -> PaymentResult:
        pass

    @abstractmethod
    def verify_webhook(self, payload: dict, signature: str) -> bool:
        pass

    @abstractmethod
    def get_status(self, external_id: str) -> str:
        pass
