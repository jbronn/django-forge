django-forge
============

Quickstart
----------

For those with short attention spans, the following creates a full mirror of
the Puppet Forge:

    $ virtualenv forge
    $ source forge/bin/activate
    $ pip install django-forge
    $ django-admin.py syncdb --noinput --settings=forge.settings
    $ django-admin.py mirror_forge --settings=forge.settings
    $ FORGE_DEBUG=1 django-admin.py runserver --settings=forge.settings

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
version (v1) of the JSON web services necessary to house (or mirror) a
private, stand-alone version of the Forge.

The Puppet Forge "standard" is undocumented, and the resources here were
reverse-engineered from the behavior of the current API endpoints (which
are buried in the Puppet module tool source code).  Care is taken to
try and imitate the behavior of the Forge whenever possible.

Simplicity and ease-of-use are the goals of this package.
