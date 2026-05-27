"""Organization middleware for strict multi-tenancy."""
from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Callable

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

if TYPE_CHECKING:
    from apps.organizations.models import Organization

_thread_locals = threading.local()


def get_current_organization() -> Organization | None:
    """Return the organization bound to the current request/thread."""
    return getattr(_thread_locals, "organization", None)


def set_current_organization(organization: Organization | None) -> None:
    """Bind organization to current thread context."""
    _thread_locals.organization = organization


def bind_organization_to_request(request: HttpRequest) -> bool:
    """
    Resolve organization from header or default membership.
    Must run after JWT/auth (DRF), not only in Django middleware.
    """
    if getattr(request, "organization", None) is not None:
        return True

    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False

    org_id = request.META.get("HTTP_X_ORGANIZATION_ID") or request.GET.get("organization_id")
    membership = None

    if org_id:
        membership = (
            user.memberships.filter(organization_id=org_id, is_active=True)
            .select_related("organization")
            .first()
        )
    else:
        membership = (
            user.memberships.filter(is_active=True, is_default=True)
            .select_related("organization")
            .first()
        )
        if not membership:
            membership = (
                user.memberships.filter(is_active=True)
                .select_related("organization")
                .first()
            )

    if membership:
        set_current_organization(membership.organization)
        request.organization = membership.organization
        request.membership = membership
        return True

    return False


class OrganizationMiddleware(MiddlewareMixin):
    """
    Resolves organization from authenticated user's membership
    or X-Organization-ID header (for API clients).
    """

    HEADER_NAME = "HTTP_X_ORGANIZATION_ID"

    def process_request(self, request: HttpRequest) -> None:
        set_current_organization(None)
        bind_organization_to_request(request)

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        set_current_organization(None)
        return response
