"""WSGI config for WhatBot Pro."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whatbot_pro.settings.prod")

application = get_wsgi_application()
