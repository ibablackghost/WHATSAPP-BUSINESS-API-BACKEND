from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.bots.api.views import BotFlowViewSet

router = DefaultRouter()
router.register("flows", BotFlowViewSet, basename="bot-flow")

urlpatterns = [path("", include(router.urls))]
