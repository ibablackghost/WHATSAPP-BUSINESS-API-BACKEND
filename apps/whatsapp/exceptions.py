"""WhatsApp domain exceptions."""


class WhatsAppNotConfiguredError(Exception):
    """Organization has no valid WhatsApp credentials."""

    def __init__(self, message: str = "WhatsApp non configuré pour cette organisation.") -> None:
        super().__init__(message)


class WhatsAppCredentialError(Exception):
    """Meta rejected the stored or submitted credentials."""

    def __init__(self, message: str, *, code: int | None = None) -> None:
        super().__init__(message)
        self.code = code
