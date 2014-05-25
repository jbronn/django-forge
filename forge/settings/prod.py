from .base import *
from .secret_key import SECRET_KEY

DEBUG = False
TEMPLATE_DEBUG = DEBUG

STATIC_ROOT = os.path.join(FORGE_ROOT, 'static')
