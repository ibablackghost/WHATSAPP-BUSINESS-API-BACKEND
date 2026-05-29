"""WSGI config for WhatBot Pro."""
import os

from django.core.wsgi import get_wsgi_application

from whatbot_pro.settings.bootstrap import apply_default_settings

apply_default_settings()

application = get_wsgi_application()
