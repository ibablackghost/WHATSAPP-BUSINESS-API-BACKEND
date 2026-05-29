"""Production settings."""
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .database import build_databases

DEBUG = False
SECURE_SSL_REDIRECT = True
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
