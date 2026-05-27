"""AES encryption service for sensitive fields."""
from __future__ import annotations

import base64
import hashlib
import logging

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

logger = logging.getLogger(__name__)


def _derive_key_from_secret() -> bytes:
    """Derive a valid Fernet key from SECRET_KEY (dev fallback)."""
    derived = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(derived)


def _resolve_fernet_key() -> bytes:
    raw = (settings.FIELD_ENCRYPTION_KEY or "").strip()
    if raw:
        key_bytes = raw.encode() if isinstance(raw, str) else raw
        try:
            Fernet(key_bytes)
            return key_bytes
        except ValueError:
            if settings.DEBUG:
                logger.warning(
                    "FIELD_ENCRYPTION_KEY invalide — utilisation d'une clé dérivée "
                    "de SECRET_KEY (mode développement uniquement)."
                )
            else:
                raise ValueError(
                    "FIELD_ENCRYPTION_KEY doit être une clé Fernet valide "
                    "(générer avec: python -c \"from cryptography.fernet import "
                    "Fernet; print(Fernet.generate_key().decode())\")"
                ) from None
    return _derive_key_from_secret()


class EncryptionService:
    """Encrypt/decrypt secrets using Fernet (AES-128-CBC)."""

    def __init__(self) -> None:
        self._fernet = Fernet(_resolve_fernet_key())

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            raise ValueError("Invalid encrypted data") from exc


encryption_service = EncryptionService()
