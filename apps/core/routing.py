from django.urls import re_path

from apps.core.consumers import RootWebSocketConsumer

websocket_urlpatterns = [
    re_path(r"ws/?$", RootWebSocketConsumer.as_asgi()),
]
