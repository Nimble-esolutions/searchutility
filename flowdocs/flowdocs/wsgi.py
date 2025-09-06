"""
WSGI config for flowdocs project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Set the settings module based on environment
if os.getenv('DJANGO_SETTINGS_MODULE'):
    # Use environment variable if set
    pass
elif os.path.exists('/app/flowdocs/flowdocs/settings_production.py'):
    # Production environment - use production settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdocs.flowdocs.settings_production')
elif os.path.exists('flowdocs/settings_production.py'):
    # Local development with production settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdocs.settings_production')
else:
    # Development environment - use regular settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdocs.settings')

application = get_wsgi_application()
