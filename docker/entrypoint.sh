#!/bin/sh
set -e

PORT="${PORT:-8000}"
mkdir -p /app/staticfiles

echo "DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}"
echo "Starting Daphne on 0.0.0.0:${PORT}"

exec daphne -b 0.0.0.0 -p "${PORT}" whatbot_pro.asgi:application
