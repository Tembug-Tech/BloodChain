"""
ASGI config for BloodChain project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodchain.settings')

application = get_asgi_application()
