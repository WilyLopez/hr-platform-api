#!/bin/sh
set -e

# collectstatic y migrate necesitan las variables de entorno reales
# (SECRET_KEY, DATABASE_URL), que solo existen en tiempo de ejecucion,
# no durante el build de la imagen. Por eso corren aqui y no en el Dockerfile.
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Idempotente: crea los roles y planes base si no existen todavia. Sin esto
# el registro publico de una empresa falla porque no encuentra el rol
# "PROPIETARIO" ni ningun plan.
python manage.py seed_datos_base

# Datos de demostracion (superadmin, 3 empresas con admins y empleados de
# ejemplo). Idempotente a nivel de empresa: si el RUC ya existe, se omite.
# Para un despliegue real (no una demo academica) esta linea se debe quitar.
python manage.py seed_demo_data

exec gunicorn config.asgi:application \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
