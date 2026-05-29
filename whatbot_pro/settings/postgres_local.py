"""
Dev local avec PostgreSQL + Redis (Docker).

Usage:
  docker compose -f docker-compose.postgres.yml up -d
  DJANGO_SETTINGS_MODULE=whatbot_pro.settings.postgres_local (dans .env)
"""
from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# PostgreSQL — variables POSTGRES_* dans .env (port 5433 via Docker)
# (DATABASES hérité de base.py)

# Redis + WebSockets temps réel
REDIS_URL = config("REDIS_URL", default="redis://localhost:6380/0")  # noqa: F405
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    },
}

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6380/1")  # noqa: F405
CELERY_RESULT_BACKEND = config(  # noqa: F405
    "CELERY_RESULT_BACKEND", default="redis://localhost:6380/2"
)
CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", default=True, cast=bool)  # noqa: F405
CELERY_TASK_EAGER_PROPAGATES = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    },
}

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

WHATSAPP_WEBHOOK_SKIP_SIGNATURE = config(  # noqa: F405
    "WHATSAPP_WEBHOOK_SKIP_SIGNATURE", default=True, cast=bool
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "1000/hour",
    "user": "10000/hour",
    "auth": "100/minute",
    "webhook": "10000/hour",
}

CORS_ALLOWED_ORIGINS = config(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
    cast=Csv(),
)
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
