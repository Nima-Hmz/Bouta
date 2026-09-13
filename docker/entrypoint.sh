#!/bin/bash
set -e

echo "Running migrations..."

python3 manage.py migrate --database=default
python3 manage.py migrate --database=content_db
python3 manage.py migrate --database=services_db

echo "Starting Django..."

exec python3 manage.py runserver 0.0.0.0:8000