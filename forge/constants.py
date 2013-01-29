import os

# Can override where the forge files are placed with FORGE_ROOT environment.
FORGE_ROOT = os.environ.get(
    'FORGE_ROOT',
    os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
)

PUPPET_FORGE = 'https://forge.puppetlabs.com'
MODULES_JSON = '/modules.json'
RELEASES_JSON = '/api/v1/releases.json'
RELEASES_ROOT = '/system/releases/'
