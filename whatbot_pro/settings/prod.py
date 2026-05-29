"""Production settings."""
import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .database import build_databases

DEBUG = False

# Railway : domaine public sans port dans l'URL (HTTPS sur 443)
_railway_public = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
_extra_hosts: list[str] = []
if _railway_public:
    _extra_hosts.append(_railway_public)
if os.environ.get("RAILWAY_ENVIRONMENT"):
    _extra_hosts.extend([".railway.app", ".up.railway.app"])

ALLOWED_HOSTS = list(
    dict.fromkeys(
        h.strip()
        for h in (*ALLOWED_HOSTS, *_extra_hosts)
        if h and str(h).strip()
    )
)

_csrf_origins: list[str] = []
if _railway_public:
    _csrf_origins.append(f"https://{_railway_public}")
_csrf_env = os.environ.get("CSRF_TRUSTED_ORIGINS", "").strip()
if _csrf_env:
    _csrf_origins.extend(origin.strip() for origin in _csrf_env.split(",") if origin.strip())
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(_csrf_origins))
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)  # noqa: F405
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Toujours PostgreSQL en prod (Railway DATABASE_URL)
DATABASES = build_databases()
_engine = DATABASES["default"]["ENGINE"]
if "sqlite" in _engine:
    raise ImproperlyConfigured(  # noqa: F405
        "SQLite interdit en production. "
        "Liez PostgreSQL sur Railway (DATABASE_URL) et utilisez "
        "DJANGO_SETTINGS_MODULE=whatbot_pro.settings.prod"
    )
