from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.contacts.api.views import ContactViewSet

router = DefaultRouter()
router.register("", ContactViewSet, basename="contact")

urlpatterns = [path("", include(router.urls))]
