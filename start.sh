#!/bin/bash

# Exit on any error
set -e

echo "Starting FlowDocs application..."

# Wait for database to be ready
echo "Waiting for database..."
python flowdocs/manage.py migrate --check || {
    echo "Database not ready, running migrations..."
    python flowdocs/manage.py migrate
}

# Create superuser if it doesn't exist
echo "Checking for superuser..."
python flowdocs/manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Collect static files
echo "Collecting static files..."
python flowdocs/manage.py collectstatic --noinput

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile - flowdocs.wsgi:application
