from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.agents.api.views import AgentPresenceViewSet

router = DefaultRouter()
router.register("presence", AgentPresenceViewSet, basename="agent-presence")

urlpatterns = [path("", include(router.urls))]
