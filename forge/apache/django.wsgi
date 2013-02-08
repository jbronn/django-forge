import os
import sys

# Ensure `forge` is in the PYTHONPATH.
FORGE_PYTHONPATH = os.path.realpath(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)
if not FORGE_PYTHONPATH in sys.path:
    sys.path.append(FORGE_PYTHONPATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forge.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
