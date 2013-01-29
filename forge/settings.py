import os

from .constants import FORGE_HOME, FORGE_ROOT, RELEASES_URL

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DB_ROOT = os.path.join(FORGE_ROOT, 'db')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DB_ROOT, 'forge.db'),
    }
}

SITE_ID = 1
TIME_ZONE = 'America/Los_Angeles'

MEDIA_ROOT = os.path.join(FORGE_ROOT, 'releases')
MEDIA_URL = RELEASES_URL
STATIC_URL = '/static/'

ROOT_URLCONF = 'forge.urls'

TEMPLATE_DIRS = (
    os.path.join(FORGE_HOME, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'forge',
)

## Hacks for simpler deployments.

# Create DB_ROOT if it doesn't exist.
if not os.path.isdir(DB_ROOT):
    os.makedirs(DB_ROOT, mode=0750)

# Create MEDIA_ROOT (used to hold the module releases) if it doesn't exist.
if not os.path.isdir(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT, mode=0750)

# Not perfect, but prevents SECRET_KEY (generated the way Django does it)
# from being included in this repo and distributed to the world.  Contributes
# to a seamless "out of the box" experience.
settings_secret = os.path.join(FORGE_ROOT, 'settings_secret.py')
if not os.path.isfile(settings_secret):
    import random
    _sysrand = random.SystemRandom()
    _secret = ''.join(
        [_sysrand.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
         for i in range(50)])
    with open(settings_secret, 'w') as fh:
        fh.write("SECRET_KEY = '%s'\n" % _secret)
from .settings_secret import SECRET_KEY
