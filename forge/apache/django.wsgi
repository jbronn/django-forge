import os
import sys

FORGE_PYTHONPATH = os.path.realpath(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..')
    )
)

sys.path.append(FORGE_PYTHONPATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'forge.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
