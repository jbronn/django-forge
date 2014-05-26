import os

from ..constants import FORGE_HOME, RELEASES_URL

# Can override where the forge files are placed with FORGE_ROOT environment.
FORGE_ROOT = os.environ.get('FORGE_ROOT', FORGE_HOME)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(FORGE_ROOT, 'forge.db'),
    }
}

SITE_ID = 1
TIME_ZONE = 'America/Los_Angeles'

MEDIA_ROOT = os.path.join(FORGE_ROOT, 'releases')
MEDIA_URL = RELEASES_URL
STATIC_URL = '/static/'
STATIC_ROOT = ''

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

ALLOWED_HOSTS = ['*']
