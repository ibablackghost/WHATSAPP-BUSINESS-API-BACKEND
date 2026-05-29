from django.conf import settings
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from whatbot_pro.settings.database import database_host_hint


class LiveHealthView(APIView):
    """Réponse immédiate pour sonde Railway (sans accès DB)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "settings_module": settings.SETTINGS_MODULE,
            }
        )


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        db_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False
        status_code = 200 if db_ok else 503
        payload = {
            "status": "healthy" if db_ok else "unhealthy",
            "database": db_ok,
            "database_target": database_host_hint(),
            "settings_module": settings.SETTINGS_MODULE,
        }
        return Response(payload, status=status_code)
