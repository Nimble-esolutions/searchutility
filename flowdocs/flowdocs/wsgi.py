"""
WSGI config for flowdocs project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add debugging
print(f"WSGI: Current working directory: {os.getcwd()}")
print(f"WSGI: Python path: {sys.path[:3]}...")

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
    print(f"WSGI: Added to Python path: {BASE_DIR}")

from django.core.wsgi import get_wsgi_application

# Set the settings module based on environment
if os.getenv('DJANGO_SETTINGS_MODULE'):
    # Use environment variable if set
    print(f"WSGI: Using environment variable: {os.getenv('DJANGO_SETTINGS_MODULE')}")
elif os.path.exists('/app/flowdocs/flowdocs/settings_production.py'):
    # Production environment - use production settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdocs.flowdocs.settings_production')
    print("WSGI: Using production settings (nested path)")
elif os.path.exists('/app/flowdocs/settings_production.py'):
    # Alternative production path
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdocs.settings_production')
    print("WSGI: Using production settings (flat path)")
elif os.path.exists('flowdocs/settings_production.py'):
    # Local development with production settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdocs.settings_production')
    print("WSGI: Using production settings (local)")
else:
    # Development environment - use regular settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdocs.settings')
    print("WSGI: Using development settings")

print(f"WSGI: Final DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

application = get_wsgi_application()
