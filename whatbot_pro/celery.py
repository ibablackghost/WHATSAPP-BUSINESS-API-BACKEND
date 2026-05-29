"""Celery application configuration."""
import os

from celery import Celery

from whatbot_pro.settings.bootstrap import apply_default_settings

apply_default_settings()

app = Celery("whatbot_pro")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
