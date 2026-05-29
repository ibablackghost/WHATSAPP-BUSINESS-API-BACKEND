FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

FROM base AS development
ENV DJANGO_SETTINGS_MODULE=whatbot_pro.settings.dev
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base AS production
ENV DJANGO_SETTINGS_MODULE=whatbot_pro.settings.prod \
    WEB_CONCURRENCY=2
RUN chmod +x /app/docker/entrypoint.sh
# Railway injecte PORT (souvent 8080) — Daphne lit $PORT dans entrypoint.sh
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD sh -c 'curl -f "http://127.0.0.1:${PORT:-8080}/health/live/" || exit 1'
ENTRYPOINT ["/app/docker/entrypoint.sh"]
