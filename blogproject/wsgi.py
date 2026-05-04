"""
WSGI config for blogproject project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogproject.settings')

application = get_wsgi_application()

if os.environ.get('VERCEL'):
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0)
