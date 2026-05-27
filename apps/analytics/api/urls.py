from django.urls import path

from apps.analytics.api.views import (
    AgentStatsView,
    DashboardKPIsView,
    ExportConversationsView,
)

urlpatterns = [
    path("dashboard/", DashboardKPIsView.as_view(), name="analytics-dashboard"),
    path("agents/", AgentStatsView.as_view(), name="analytics-agents"),
    path("export/conversations/", ExportConversationsView.as_view(), name="analytics-export"),
]
