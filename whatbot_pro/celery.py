"""Celery application configuration."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whatbot_pro.settings.local")

app = Celery("whatbot_pro")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
