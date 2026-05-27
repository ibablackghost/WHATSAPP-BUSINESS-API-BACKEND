"""
Configuration locale sans Docker.

- SQLite (fichier db.sqlite3)
- Pas de Redis requis (WebSockets en mémoire, Celery synchrone)
- Idéal pour développement rapide sur Windows/Mac/Linux
"""
from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# --- Base de données SQLite (aucune installation PostgreSQL) ---
USE_SQLITE = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# --- Pas de Redis : tout en local / mémoire ---
USE_REDIS = False

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Celery Beat : stockage des tâches planifiées dans SQLite
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "1000/hour",
    "user": "10000/hour",
    "auth": "100/minute",
    "webhook": "10000/hour",
}

# --- CORS (Next.js : localhost ET 127.0.0.1, ports 3000-3001) ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-organization-id",
]
CORS_EXPOSE_HEADERS = ["content-type", "authorization"]
