from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

## Hacks for simpler deployments.

# Create MEDIA_ROOT (used to hold the module releases) if it doesn't exist.
if not (os.path.isdir(MEDIA_ROOT) or os.path.islink(MEDIA_ROOT)):
    os.makedirs(MEDIA_ROOT, mode=0755)

# Not perfect, but prevents SECRET_KEY (generated the way Django does it)
# from being included in this repo and distributed to the world.  Contributes
# to a seamless "out of the box" experience.
settings_key = os.path.join(os.path.dirname(__file__), 'key.py')
if not os.path.isfile(settings_key):
    from .secret_key import secret_key_file
    secret_key_file(settings_key)
from .key import SECRET_KEY
