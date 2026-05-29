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
# Railway injecte PORT (souvent != 8000) — ne pas binder en dur sur 8000
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD sh -c 'curl -f "http://127.0.0.1:${PORT:-8000}/health/" || exit 1'
CMD ["sh", "-c", "exec gunicorn whatbot_pro.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8000} -w ${WEB_CONCURRENCY}"]
