import re
import os

# Where module is on filesystem.
FORGE_HOME = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))

MODULE_REGEX = re.compile(r'^(?P<author>\w+)[/\-](?P<module>\w+)$')
TARBALL_REGEX = re.compile(r'^(?P<author>\w+)-(?P<module>\w+)-(?P<version>[\w\.]+)\.tar\.gz$')

PUPPET_FORGE = 'https://forge.puppetlabs.com'
MODULES_JSON = '/modules.json'
RELEASES_JSON = '/api/v1/releases.json'
RELEASES_URL = '/system/releases/'
