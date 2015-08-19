django-forge
============

Quickstart
----------

For those with short attention spans, the following creates a full mirror of
the Puppet Forge:

    $ virtualenv forge
    $ source forge/bin/activate
    $ pip install django-forge
    $ django-admin.py migrate --noinput --settings=forge.settings.dev
    $ django-admin.py sync_forge --settings=forge.settings.dev
    $ django-admin.py runserver --settings=forge.settings.dev

Point your Puppet configuration file (`/etc/puppet.conf` or
`~/.puppet/puppet.conf`) to the forge:

    [main]
        module_repository = http://localhost:8000

You should now be able search and install with `puppet module`.

Publishing can be done with interface at `/admin/` -- create an account
with:

    $ ./manage.py createsuperuser

Background
----------

The Puppet Forge (https://forge.puppetlabs.com/) is a central authority for
finding and installing Puppet modules.  This package implements the first
version (v1) and third version (v3) of the JSON web services necessary to house
(or mirror) a private, stand-alone version of the Forge.


Simplicity and ease-of-use are goals of this package.

### v1

This version of the Puppet Forge is undocumented, and the resources here were
reverse-engineered from the behavior of the current API endpoints (which
are buried in the Puppet module tool source code).  Care is taken to
try and imitate the behavior of this API whenever possible.

### v3

Puppet Labs fully documented and shared the v3 standard with the community,
see https://forgeapi.puppetlabs.com for further details.  This package
only implements the subset of this API necessary to talk to open source
Puppet 3.6+ clients.
