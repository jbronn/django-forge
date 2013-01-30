import re
import os

# Can override where the forge files are placed with FORGE_ROOT environment.
FORGE_HOME = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
FORGE_ROOT = os.environ.get('FORGE_ROOT', FORGE_HOME)

MODULE_REGEX = re.compile(r'^(?P<author>\w+)[/\-](?P<module>\w+)$')
TARBALL_REGEX = re.compile(r'^(?P<author>\w+)-(?P<module>\w+)-(?P<version>[\w\.]+)\.tar\.gz$')

PUPPET_FORGE = 'https://forge.puppetlabs.com'
MODULES_JSON = '/modules.json'
RELEASES_JSON = '/api/v1/releases.json'
RELEASES_URL = '/system/releases/'
