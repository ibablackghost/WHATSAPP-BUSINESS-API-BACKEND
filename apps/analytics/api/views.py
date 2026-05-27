from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.services.analytics_service import AnalyticsService
from apps.core.api.permissions import IsOrganizationMember


class DashboardKPIsView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        kpis = AnalyticsService().get_dashboard_kpis(request.organization.id, days)
        return Response(kpis)


class AgentStatsView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        stats = AnalyticsService().get_agent_stats(request.organization.id, days)
        return Response(stats)


class ExportConversationsView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        csv_data = AnalyticsService().export_conversations_csv(request.organization.id)
        response = HttpResponse(csv_data, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="conversations.csv"'
        return response
