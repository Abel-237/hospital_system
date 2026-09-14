#!/bin/bash
set -e

echo "=== Waiting for PostgreSQL if configured ==="
# Execute migrations
echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Compiling translation catalogs ==="
python manage.py compilemessages || echo "Translation files compilation finished."

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear

exec "$@"
