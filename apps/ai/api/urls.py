from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.ai.api.views import AIChatView, FAQEntryViewSet, SemanticSearchView

router = DefaultRouter()
router.register("faq", FAQEntryViewSet, basename="faq")

urlpatterns = [
    path("", include(router.urls)),
    path("chat/", AIChatView.as_view(), name="ai-chat"),
    path("search/", SemanticSearchView.as_view(), name="ai-search"),
]
