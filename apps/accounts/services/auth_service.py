"""Authentication service with JWT and 2FA."""
from __future__ import annotations

import io
from typing import TYPE_CHECKING

import pyotp
import qrcode
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models.audit import AuditLog
from apps.core.services.events import DomainEvent, event_bus

if TYPE_CHECKING:
    from apps.accounts.models import User


class AuthService:
    def authenticate_user(
        self, email: str, password: str, totp_code: str | None = None
    ) -> tuple[User | None, dict | None, str | None]:
        user = authenticate(username=email, password=password)
        if not user:
            return None, None, "Invalid credentials"

        if user.totp_enabled:
            if not totp_code:
                return user, None, "2FA required"
            totp = pyotp.TOTP(user.totp_secret)
            if not totp.verify(totp_code, valid_window=1):
                return None, None, "Invalid 2FA code"

        tokens = self._generate_tokens(user)
        event_bus.publish(
            DomainEvent(
                event_type="user.logged_in",
                payload={"user_id": str(user.id)},
            )
        )
        return user, tokens, None

    def _generate_tokens(self, user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    def setup_totp(self, user: User) -> dict:
        secret = pyotp.random_base32()
        user.totp_secret = secret
        user.save(update_fields=["totp_secret"])
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email, issuer_name="WhatBot Pro"
        )
        qr = qrcode.make(provisioning_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        import base64

        return {
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "qr_code_base64": base64.b64encode(buffer.getvalue()).decode(),
        }

    def confirm_totp(self, user: User, code: str) -> bool:
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code, valid_window=1):
            user.totp_enabled = True
            user.save(update_fields=["totp_enabled"])
            return True
        return False

    def log_audit(
        self,
        user: User | None,
        action: str,
        request,
        **metadata,
    ) -> None:
        from apps.core.middleware.organization import get_current_organization

        AuditLog.objects.create(
            user=user,
            organization=get_current_organization(),
            action=action,
            ip_address=getattr(request, "audit_context", {}).get("ip_address"),
            user_agent=getattr(request, "audit_context", {}).get("user_agent", ""),
            metadata=metadata,
        )
