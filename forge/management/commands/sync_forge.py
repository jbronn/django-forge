import hashlib
import logging
import os
import sys
import urllib
import urlparse
from contextlib import closing
from optparse import make_option

from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import Count

from forge import constants
from forge.client import ForgeAPI, ForgeClient
from forge.models import Author, Module, Release


logger = logging.getLogger('forge.sync')


class Command(BaseCommand):
    help = (
        'Syncs with another Puppet Forge.'
    )

    option_list = BaseCommand.option_list + (
        make_option(
            '--api-url',
            action='store',
            dest='api_url',
            default=constants.PUPPETLABS_FORGE_API_URL,
            help=("Puppet Forge URL to mirror, defaults to: %s." %
                  constants.PUPPETLABS_FORGE_API_URL),
        ),
        make_option(
            '-q', '--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help=('Silence all output (sets verbosity to 0).'),
        ),
        make_option(
            '-t', '--throttle',
            action='store',
            dest='throttle',
            default=0.5,
            type='float',
            help=('Time (in seconds) to wait between API requests.'),
        ),
    )

    def handle(self, *args, **options):
        if options['quiet']:
            self.verbosity = 0
        else:
            self.verbosity = int(options['verbosity'])

        self.client = ForgeClient(api_url=options['api_url'],
                                  throttle=options['throttle'])

        # Sync authors first, then modules, and finally create releases
        # after downloading the module tarballs.
        self.sync_authors()
        self.sync_modules()
        self.sync_releases()

    def log(self, msg, error=False, verbosity_level=1):
        if error:
            logger.error(msg)
        else:
            logger.info(msg)
        if self.verbosity >= verbosity_level:
            sys.stdout.write('%s\n' % msg)

    def sync_authors(self):
        self.users_api = ForgeAPI('users', client=self.client)

        for user in self.users_api:
            if user['module_count'] > 0:
                author, created = Author.objects.get_or_create(
                    name=user['username']
                )
                if created:
                    self.log('Created Author: %s' % author)

    def sync_modules(self):
        self.modules_api = ForgeAPI('modules', client=self.client)

        for mod in self.modules_api:
            module, created = Module.objects.get_or_create(
                author=Author.objects.get_by_natural_key(mod['owner']['username']),
                name=mod['name']
            )
            if created:
                msg = 'Created Module: %s' % module
                self.log(msg)

            desc = mod['current_release']['metadata'].get('description', '')
            tags = ' '.join(mod['current_release']['tags'])

            if tags != module.tags or desc != module.desc:
                if not created:
                    if tags != module.tags:
                        self.log(
                            '\n'.join(
                                [' Tags Differ:',
                                 '  Old: %s' % module.tags,
                                 '  New: %s' % tags]),
                            verbosity_level=2
                        )

                    if desc != module.desc:
                        self.log(
                            '\n'.join(
                                [' Descriptions Differ:',
                                 '  Old: %s' % module.desc,
                                 '  New: %s' % desc]),
                            verbosity_level=2
                        )

                module.tags = tags
                module.desc = desc
                module.save()

                if not created:
                    self.log('Updated Module: %s' % module)


    def sync_releases(self):
        # Only synchronize releases from authors that have released at least
        # one Puppet module.  Querying the releases by author should make it
        # so that less total API calls are requested of the remote forge.
        module_authors = Author.objects.annotate(
            num_modules=Count('module')
        ).filter(num_modules__gt=0).distinct()

        for author in module_authors.iterator():
            author_name = author.name.lower()
            alpha = author_name[0].lower()

            releases_api = ForgeAPI(
                'releases', client=self.client,
                query={'owner': author_name,
                       'sort_by': 'release_date'}
            )

            for rel in releases_api:
                tarball = os.path.basename(rel['file_uri'])

                # TODO: Change to v3 compatible file structure, this is using the
                #  the same structure that v1 does.
                upload_to = '/'.join([alpha, author_name, tarball])
                destination = os.path.join(settings.MEDIA_ROOT, upload_to)
                destination_tmp = destination + '.tmp'

                dest_dir = os.path.dirname(destination)
                if not os.path.isdir(dest_dir):
                    os.makedirs(dest_dir, mode=0755)

                if not os.path.isfile(destination):
                    tarball_url = urlparse.urljoin(
                        self.client.api_url, rel['file_uri']
                    )

                    file_md5 = hashlib.md5()
                    with open(destination_tmp, 'wb') as tb_h:
                        with closing(self.client.get(tarball_url, stream=True)) as req:
                            for chunk in req:
                                if chunk:
                                    tb_h.write(chunk)
                                    file_md5.update(chunk)

                    if file_md5.hexdigest() == rel['file_md5']:
                        os.rename(destination_tmp, destination)
                        self.log('Downloaded Release: %s' % tarball)
                    else:
                        os.remove(destination_tmp)
                        self.log(
                            'Downloaded corrupt data from: %s' % tarball_url,
                            error=True
                        )
                        continue

                # Get corresponding module.
                module = Module.objects.get(
                    author=author, name=rel['module']['name']
                )

                # Creating Release now download is completed.
                try:
                    release, created = Release.objects.get_or_create(
                        module=module, version=rel['version'], tarball=upload_to
                    )
                    if created:
                        self.log('Created Release: %s' % release)
                except Exception as e:
                    err_msg = (
                        'Could not create release for: %s version %s\n' %
                        (module, rel['version'])
                    )
                    self.log(err_msg, error=True)
