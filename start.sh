#!/bin/sh
set -e

# collectstatic y migrate necesitan las variables de entorno reales
# (SECRET_KEY, DATABASE_URL), que solo existen en tiempo de ejecucion,
# no durante el build de la imagen. Por eso corren aqui y no en el Dockerfile.
python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec gunicorn config.asgi:application \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
