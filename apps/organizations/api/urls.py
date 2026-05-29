from django.urls import path

from apps.organizations.api.views import (
    CurrentOrganizationView,
    OrganizationListCreateView,
    OrganizationWhatsAppConfigView,
    OrganizationWhatsAppStatusView,
)

urlpatterns = [
    path("", OrganizationListCreateView.as_view(), name="organization-list"),
    path("current/", CurrentOrganizationView.as_view(), name="organization-current"),
    path(
        "whatsapp-config/",
        OrganizationWhatsAppConfigView.as_view(),
        name="organization-whatsapp-config",
    ),
    path(
        "whatsapp-config/status/",
        OrganizationWhatsAppStatusView.as_view(),
        name="organization-whatsapp-status",
    ),
]
