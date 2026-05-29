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
ENV DJANGO_SETTINGS_MODULE=whatbot_pro.settings.prod
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1
CMD ["gunicorn", "whatbot_pro.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "-w", "4"]
