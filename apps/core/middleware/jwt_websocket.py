"""JWT authentication for WebSocket connections (?token= or ?access_token=)."""
from __future__ import annotations

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def _get_user_from_token(token_str: str) -> User | AnonymousUser:
    try:
        token = AccessToken(token_str)
        return User.objects.get(id=token["user_id"])
    except (TokenError, User.DoesNotExist, KeyError):
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    """Authenticate WebSocket via JWT query param (overrides session when present)."""

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            query = parse_qs(scope.get("query_string", b"").decode())
            token = (query.get("token") or query.get("access_token") or [None])[0]
            if token:
                scope["user"] = await _get_user_from_token(token)
        return await self.inner(scope, receive, send)
