import contextlib
import os
import sys
import urllib
from optparse import make_option

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils import simplejson

from forge import constants
from forge.models import Author, Module, Release


class Command(BaseCommand):
    help = (
        'Mirrors the Puppet Forge.'
    )

    option_list = BaseCommand.option_list + (
        make_option(
            '--url',
            action='store',
            dest='url',
            default=constants.PUPPET_FORGE,
            help=("Puppet Forge URL to mirror, defaults to: %s." %
                  constants.PUPPET_FORGE),
        ),
        make_option(
            '--modules-json',
            action='store',
            dest='modules_json',
            default=None,
            help=("Use the given JSON file instead of downloading it."),
        ),
        make_option(
            '-q', '--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help=("Silence all output (sets verbosity to 0)."),
        ),
    )

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])
        if options['quiet']:
            self.verbosity = 0

        if options['modules_json']:
            with open(options['modules_json'], 'r') as json_h:
                modules_raw = json_h.read()
        else:
            if self.verbosity:
                sys.stdout.write('Downloading modules.json from %s... ' %
                                  options['url'])
                sys.stdout.flush()
            modules_url = options['url'] + constants.MODULES_JSON
            with contextlib.closing(urllib.urlopen(modules_url)) as json_h:
                modules_raw = json_h.read()

            if self.verbosity:
                sys.stdout.write('Done\n')
                sys.stdout.flush()
        data = simplejson.loads(modules_raw)

        # Cache variables.
        self.authors = {}
        self.modules = {}

        # Sync authors first, then modules, and finally create releases
        # after downloading the module tarballs.
        self.create_authors(data)
        self.create_modules(data)
        self.create_releases(data, options['url'])

    def create_authors(self, data):
        for module in data:
            author_name = module['author']

            # Creating Author.
            author = self.authors.get(author_name, None)
            if author is None:
                author, created = Author.objects.get_or_create(
                    name=author_name)
                if created and self.verbosity:
                    sys.stdout.write('Created Author: %s\n' % author)
                self.authors[author_name] = author

    def create_modules(self, data):
        for mod in data:
            full_name = mod['full_name']
            name = mod['name']
            author_name = mod['author']
            alpha = author_name[0].lower()
            author = self.authors.get(author_name)

            # Creating Module.
            tag_list = mod['tag_list']
            tag_list.sort()
            tags = ' '.join(tag_list)
            desc = mod['desc']
            module = self.modules.get(full_name, None)

            # Have to get or create the module.
            if module is None:
                module, created = Module.objects.get_or_create(
                    author=author, name=name)

                if self.verbosity and created:
                    sys.stdout.write('Created Module: %s\n' % module)
            else:
                created = False

            # Update or create the module's tags and description.
            if tags != module.tags or desc != module.desc:
                if not created and self.verbosity >= 2:
                    if tags != module.tags:
                        sys.stdout.write(' Tags Differ:\n')
                        sys.stdout.write('  Old: %s\n' % module.tags)
                        sys.stdout.write('  New: %s\n' % tags)

                    if desc != module.desc:
                        sys.stdout.write(' Descriptions Differ:\n')
                        sys.stdout.write('  Old: %s\n' % module.desc)
                        sys.stdout.write('  New: %s\n' % desc)

                module.tags = tags
                module.desc = desc
                module.save()

                if self.verbosity and not created:
                    sys.stdout.write('Updated Module: %s\n' % module)

            self.modules[full_name] = module

    def create_releases(self, data, url):
        for mod in data:
            module = self.modules.get(mod['full_name'])
            author_name = module.author.name
            alpha = author_name[0].lower()

            # Creating each Release for the Module -- in the order that the
            # releases were uploaded.
            releases = mod['releases']
            releases.reverse()
            for release in releases:
                version = release['version']
                tarball = '%s-%s-%s.tar.gz' % (
                    author_name, module.name, version)
                upload_to = '/'.join([alpha, author_name, tarball])
                relative = constants.RELEASES_URL + upload_to
                tarball_url = url + relative
                destination = os.path.join(settings.MEDIA_ROOT, upload_to)

                dest_dir = os.path.dirname(destination)
                if not os.path.isdir(dest_dir):
                    os.makedirs(dest_dir, mode=0755)

                if not os.path.isfile(destination):
                    with contextlib.closing(urllib.urlopen(tarball_url)) as tb_h:
                        tarball_data = tb_h.read()

                    with open(destination, 'wb') as tb_h:
                        tb_h.write(tarball_data)

                    if self.verbosity:
                        sys.stdout.write('Downloaded Release: %s\n' %
                                         os.path.basename(destination))

                # Creating Release now download is completed.
                release, created = Release.objects.get_or_create(
                    module=module, version=version, tarball=upload_to)
                if created and self.verbosity:
                    sys.stdout.write('Created Release: %s\n' % release)
