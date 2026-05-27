from django.urls import re_path

from apps.agents.consumers import AgentConsumer

websocket_urlpatterns = [
    re_path(r"ws/agents/$", AgentConsumer.as_asgi()),
]
