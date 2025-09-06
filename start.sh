#!/bin/bash

# Exit on any error
set -e

echo "Starting FlowDocs application..."

# Set default environment variables if not set
export SECRET_KEY=${SECRET_KEY:-"django-insecure-change-me-in-production"}
export DEBUG=${DEBUG:-"True"}
export ALLOWED_HOSTS=${ALLOWED_HOSTS:-"*"}
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"flowdocs.settings"}

echo "Environment: SECRET_KEY=${SECRET_KEY:0:10}..., DEBUG=$DEBUG, ALLOWED_HOSTS=$ALLOWED_HOSTS, DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Run migrations (ignore errors for now)
echo "Running database migrations..."
cd /app/flowdocs && DJANGO_SETTINGS_MODULE=flowdocs.settings python manage.py migrate || {
    echo "Migration failed, continuing with existing database..."
}

# Create superuser if it doesn't exist (ignore errors)
echo "Checking for superuser..."
cd /app/flowdocs && DJANGO_SETTINGS_MODULE=flowdocs.settings python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
" || echo "Superuser creation failed, continuing..."

# Collect static files
echo "Collecting static files..."
cd /app/flowdocs && DJANGO_SETTINGS_MODULE=flowdocs.settings python manage.py collectstatic --noinput || echo "Static files collection failed, continuing..."

# Start the application
echo "Starting Gunicorn server on 0.0.0.0:8000..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile - flowdocs.wsgi:application
