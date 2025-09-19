#!/bin/bash
set -e
echo "Starting FlowDocs application..."

# Environment defaults
export SECRET_KEY=${SECRET_KEY:-"django-insecure-change-me-in-production"}
export DEBUG=${DEBUG:-"True"}
export ALLOWED_HOSTS=${ALLOWED_HOSTS:-"*"}
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"flowdocs.settings"}

echo "Environment ready: DEBUG=$DEBUG, ALLOWED_HOSTS=$ALLOWED_HOSTS"

cd /app/flowdocs

# Run migrations (non-fatal)
echo "Running database migrations..."
python manage.py migrate || echo "Migration failed, skipping."

# Create superuser (non-fatal)
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
" || echo "Superuser creation failed, skipping."

# Collect static files (non-fatal)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "Static collection failed, skipping."

# Start Gunicorn (always runs)
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 flowdocs.wsgi:application
