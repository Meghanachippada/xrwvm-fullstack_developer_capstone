#!/bin/sh
set -e
echo "Running migrations & collectstatic..."
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput
python manage.py collectstatic --noinput || true
exec "$@"
