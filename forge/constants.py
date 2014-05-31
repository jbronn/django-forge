import re
import os

# Where module is on filesystem.
FORGE_HOME = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))

MODULE_REGEX = re.compile(r'^(?P<author>\w+)[/\-](?P<module>\w+)$')
TARBALL_REGEX = re.compile(r'^(?P<author>\w+)-(?P<module>\w+)-(?P<version>[\w\.]+)\.tar\.gz$')

PUPPETLABS_FORGE_URL = 'https://forge.puppetlabs.com'
PUPPETLABS_FORGE_API_URL = 'https://forgeapi.puppetlabs.com'
MODULES_JSON = '/modules.json'
RELEASES_JSON = '/api/v1/releases.json'
RELEASES_URL = '/system/releases/'
