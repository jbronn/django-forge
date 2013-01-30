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
        verbosity = int(options['verbosity'])
        if options['quiet']:
            verbosity = 0

        if options['modules_json']:
            with open(options['modules_json'], 'r') as json_h:
                modules_raw = json_h.read()
        else:
            if verbosity:
                sys.stdout.write('Downloading modules.json from %s... ' %
                                  options['url'])
                sys.stdout.flush()
            modules_url = options['url'] + constants.MODULES_JSON
            with contextlib.closing(urllib.urlopen(modules_url)) as json_h:
                modules_raw = json_h.read()
            if verbosity:
                sys.stdout.write('Done\n')
                sys.stdout.flush()
        modules_data = simplejson.loads(modules_raw)

        authors = {}
        modules = {}
        for mod in modules_data:
            name = mod['name']
            author_name = mod['author']
            alpha  = author_name[0].lower()

            # Creating Author.
            author = authors.get(author_name, None)
            if author is None:
                author, created = Author.objects.get_or_create(name=author_name)
                authors[author_name] = author

            # Creating Module.
            full_name = mod['full_name']
            tag_list = mod['tag_list']
            tag_list.sort()
            tags = ' '.join(tag_list)
            desc = mod['desc']
            module = modules.get(full_name, None)
            if module is None:
                module, created = Module.objects.get_or_create(
                    author=author, name=name)
                if tags != module.tags or desc != module.desc:
                    if verbosity:
                        sys.stdout.write('Updated Module: %s\n' % module)

                    if tags != module.tags and verbosity >= 3:
                        sys.stdout.write(' Tags Differ:\n')
                        sys.stdout.write('  Old: %s\n' % module.tags)
                        sys.stdout.write('  New: %s\n' % tags)

                    if desc != module.desc and verbosity >= 3:
                        sys.stdout.write(' Descriptoins Differ:\n')
                        sys.stdout.write('  Old: %s\n' % module.desc)
                        sys.stdout.write('  New: %s\n' % desc)

                    module.tags = tags
                    module.desc = desc
                    module.save()

            # Creating each Release for the Module -- in the order that the
            # releases were uploaded.
            releases = mod['releases']
            releases.reverse()
            for release in releases:
                version = release['version']
                tarball = '%s-%s-%s.tar.gz' % (author_name, name, version)
                upload_to = '/'.join([alpha, author_name, tarball])
                relative = constants.RELEASES_URL + upload_to
                tarball_url = options['url'] + relative
                destination = os.path.join(settings.MEDIA_ROOT, upload_to)

                dest_dir = os.path.dirname(destination)
                if not os.path.isdir(dest_dir):
                    os.makedirs(dest_dir, mode=0755)
                    if verbosity:
                        sys.stdout.write('Created: %s\n' % dest_dir)

                if not os.path.isfile(destination):
                    with contextlib.closing(urllib.urlopen(tarball_url)) as tb_h:
                        tarball_data = tb_h.read()

                    with open(destination, 'wb') as tb_h:
                        tb_h.write(tarball_data)

                    if verbosity:
                        sys.stdout.write('Downloaded: %s\n' %
                                         os.path.basename(destination))

                # Creating Release now download is completed.
                release, created = Release.objects.get_or_create(
                    module=module, version=version, tarball=upload_to)
