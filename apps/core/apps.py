from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self) -> None:
        import logging

        from django.conf import settings

        from whatbot_pro.settings.database import database_host_hint

        import apps.core.services.event_handlers  # noqa: F401 — register handlers

        logging.getLogger(__name__).info(
            "WhatBot DB: %s | settings=%s",
            database_host_hint(),
            settings.SETTINGS_MODULE,
        )
