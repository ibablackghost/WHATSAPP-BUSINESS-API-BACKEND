"""Configuration base de donnees (Railway DATABASE_URL, PG*, ou POSTGRES_*)."""
import os
from urllib.parse import parse_qs, unquote, urlparse

from decouple import config


def _env_first(*keys: str, default: str = "") -> str:
    """Variables d'environnement (Railway) prioritaires sur le fichier .env."""
    for key in keys:
        val = os.environ.get(key)
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    for key in keys:
        val = config(key, default=None)
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    return default


def _pg_from_url(database_url: str) -> dict:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    parsed = urlparse(database_url)
    query = parse_qs(parsed.query)
    options: dict[str, str] = {"connect_timeout": "10"}
    sslmode = query.get("sslmode", [None])[0]
    if sslmode:
        options["sslmode"] = sslmode
    elif os.environ.get("RAILWAY_ENVIRONMENT"):
        options["sslmode"] = "require"
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parsed.path.lstrip("/") or ""),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or 5432),
        **({"OPTIONS": options} if options else {}),
    }


def build_databases() -> dict:
    database_url = _env_first("DATABASE_URL", "DATABASE_PRIVATE_URL")
    if database_url:
        return {"default": _pg_from_url(database_url)}

    host = _env_first("POSTGRES_HOST", "PGHOST", default="localhost")
    if os.environ.get("RAILWAY_ENVIRONMENT") and host in ("localhost", "127.0.0.1"):
        host = _env_first("PGHOST", default=host)

    return {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _env_first("POSTGRES_DB", "PGDATABASE", default="whatbot_pro"),
            "USER": _env_first("POSTGRES_USER", "PGUSER", default="whatbot"),
            "PASSWORD": _env_first("POSTGRES_PASSWORD", "PGPASSWORD", default="whatbot"),
            "HOST": host,
            "PORT": _env_first("POSTGRES_PORT", "PGPORT", default="5432"),
            "OPTIONS": {
                "connect_timeout": 10,
                **(
                    {"sslmode": "require"}
                    if os.environ.get("RAILWAY_ENVIRONMENT")
                    else {}
                ),
            },
        }
    }


def database_host_hint() -> str:
    """Hote DB pour logs / health (sans secrets)."""
    db = build_databases()["default"]
    if db.get("ENGINE", "").endswith("sqlite3"):
        return f"sqlite:{db.get('NAME', '?')}"
    return f"{db.get('HOST', '?')}:{db.get('PORT', '?')}/{db.get('NAME', '?')}"
