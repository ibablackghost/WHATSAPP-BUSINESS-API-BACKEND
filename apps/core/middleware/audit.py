"""Audit middleware for request logging."""
from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin


class AuditMiddleware(MiddlewareMixin):
    """Attaches audit context to request for downstream services."""

    def process_request(self, request: HttpRequest) -> None:
        request.audit_context = {
            "ip_address": self._get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        }

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str | None:
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
