"""
WSGI config for BloodChain project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodchain.settings')

application = get_wsgi_application()
