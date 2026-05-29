"""ASGI config for WhatBot Pro with WebSocket routing."""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whatbot_pro.settings.local")

django_asgi_app = get_asgi_application()

from apps.agents.routing import websocket_urlpatterns as agent_ws  # noqa: E402
from apps.conversations.routing import websocket_urlpatterns as conversation_ws  # noqa: E402
from apps.core.middleware.jwt_websocket import JwtAuthMiddleware  # noqa: E402
from apps.core.routing import websocket_urlpatterns as core_ws  # noqa: E402
from apps.notifications.routing import websocket_urlpatterns as notification_ws  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            JwtAuthMiddleware(
                URLRouter(core_ws + conversation_ws + agent_ws + notification_ws)
            )
        ),
    }
)
