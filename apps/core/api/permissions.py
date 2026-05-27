"""Reusable DRF permissions."""
from rest_framework.permissions import BasePermission

from apps.core.middleware.organization import bind_organization_to_request


class IsOrganizationMember(BasePermission):
    """User must belong to the current organization."""

    def has_permission(self, request, view) -> bool:
        bind_organization_to_request(request)
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request, "organization")
            and request.organization is not None
        )


class HasRole(BasePermission):
    """Check user has required role in current organization."""

    required_roles: list[str] = []

    def has_permission(self, request, view) -> bool:
        bind_organization_to_request(request)
        if not hasattr(request, "membership"):
            return False
        return request.membership.role in self.required_roles


class IsAdmin(HasRole):
    required_roles = ["admin"]


class IsSupervisorOrAdmin(HasRole):
    required_roles = ["admin", "supervisor"]
