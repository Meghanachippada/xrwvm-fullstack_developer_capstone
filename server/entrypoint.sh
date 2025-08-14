#!/bin/sh
echo "Making migrations and migrating the database."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
# If collectstatic ever fails, it's okay to skip; uncomment the next line if needed:
# python manage.py collectstatic --noinput || true
exec "$@"
