from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.notifications.api.views import NotificationCampaignViewSet

router = DefaultRouter()
router.register("campaigns", NotificationCampaignViewSet, basename="campaign")

urlpatterns = [path("", include(router.urls))]
