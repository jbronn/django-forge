from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

## Hacks for simpler deployments.

# Create MEDIA_ROOT (used to hold the module releases) if it doesn't exist.
if not (os.path.isdir(MEDIA_ROOT) or os.path.islink(MEDIA_ROOT)):
    os.makedirs(MEDIA_ROOT, mode=0755)

from .secret_key import SECRET_KEY
