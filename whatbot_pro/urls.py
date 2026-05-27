"""Root URL configuration."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.api.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/v1/auth/", include("apps.accounts.api.urls")),
    path("api/v1/organizations/", include("apps.organizations.api.urls")),
    path("api/v1/contacts/", include("apps.contacts.api.urls")),
    path("api/v1/whatsapp/", include("apps.whatsapp.api.urls")),
    path("api/v1/conversations/", include("apps.conversations.api.urls")),
    path("api/v1/bots/", include("apps.bots.api.urls")),
    path("api/v1/agents/", include("apps.agents.api.urls")),
    path("api/v1/ai/", include("apps.ai.api.urls")),
    path("api/v1/payments/", include("apps.payments.api.urls")),
    path("api/v1/notifications/", include("apps.notifications.api.urls")),
    path("api/v1/analytics/", include("apps.analytics.api.urls")),
]
