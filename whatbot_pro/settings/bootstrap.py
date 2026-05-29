"""Choix du module Django selon l'environnement (Railway / local)."""
import os


def default_settings_module() -> str:
    if os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("DATABASE_URL"):
        return "whatbot_pro.settings.prod"
    return "whatbot_pro.settings.postgres_local"


def apply_default_settings() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings_module())
