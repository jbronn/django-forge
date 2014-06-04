import hashlib
import json
import os
import tarfile
import warnings

from django.db import models
from semantic_version.django_fields import VersionField

from .constants import MODULE_REGEX
from .storage import ForgeStorage


class AuthorManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Author(models.Model):
    name = models.CharField(max_length=64, unique=True)

    objects = AuthorManager()

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class ModuleManager(models.Manager):
    def get_by_natural_key(self, author, name):
        return self.get(author=Author.objects.get_by_natural_key(author),
                        name=name)

    def get_for_full_name(self, full_name):
        """
        Returns Module for the given full name, e.g., 'puppetlabs/stdlib'.
        """
        parsed = self.parse_full_name(full_name)
        if parsed:
            author, name = parsed
            return self.get(author__name=author, name=name)
        else:
            raise self.model.DoesNotExist

    def parse_full_name(self, full_name):
        """
        Return the module components given a full module name, or None.
        """
        match = MODULE_REGEX.match(full_name)
        if match:
            return (match.group('author'), match.group('module'))
        else:
            return None


class Module(models.Model):
    author = models.ForeignKey(Author)
    name = models.CharField(max_length=128, db_index=True)
    desc = models.TextField(db_index=True, blank=True)
    tags = models.TextField(db_index=True, blank=True)

    objects = ModuleManager()

    class Meta:
        unique_together = ('author', 'name')

    def __unicode__(self):
        return self.canonical_name

    @classmethod
    def parse_full_name(cls, full_name):
        """
        Return the module components given a full module name, or None.
        """
        warnings.warn('This classmethod is deprecated, please use the '
                      'manager method instead.', DeprecationWarning)
        return cls.objects.parse_full_name(full_name)

    @classmethod
    def get_for_full_name(cls, full_name):
        """
        Returns Module for the given full name, e.g., 'puppetlabs/stdlib'.
        """
        warnings.warn('This classmethod is deprecated, please use the '
                      'manager method instead.', DeprecationWarning)
        return cls.objects.get_for_full_name(full_name)

    @property
    def canonical_name(self):
        return u'%s-%s' % (self.author.name.lower(), self.name.lower())

    @property
    def legacy_name(self):
        return u'%s/%s' % (self.author.name.lower(), self.name.lower())

    @property
    def latest_release(self):
        """
        Return the latest version, preferably one that isn't a pre-release.
        """
        # First, try and get all non pre-release versions.
        releases = dict((release.version, release)
                        for release in self.releases.all()
                        if not release.version.prerelease)
        if not releases:
            # If all pre-releases, get all of them or return None.
            releases = dict((release.version, release)
                            for release in self.releases.all())
            if not releases:
                return None

        latest_version = max(releases.keys())
        return releases[latest_version]

    def natural_key(self):
        return (self.author.name, self.name)

    @property
    def tag_list(self):
        return self.tags.split()


def tarball_upload(instance, filename):
    author = instance.module.author.name
    return '/'.join([author[0].lower(), author, filename])


class Release(models.Model):
    module = models.ForeignKey(Module, related_name='releases')
    version = VersionField(db_index=True)
    tarball = models.FileField(upload_to=tarball_upload,
                               storage=ForgeStorage())

    class Meta:
        unique_together = ('module', 'version')

    def __unicode__(self):
        return u'%s version %s' % (self.module, self.version)

    @property
    def file_md5(self):
        # TODO: This will become an actual database field.
        self.tarball.open()
        file_md5 = hashlib.md5()
        file_md5.update(self.tarball.read())
        self.tarball.close()
        return file_md5.hexdigest()

    @property
    def file_size(self):
        return self.tarball.size

    @property
    def metadata_json(self):
        with tarfile.open(self.tarball.path, mode='r:gz') as tf:
            metadata_ti = None
            for fname in tf.getnames():
                if os.path.basename(fname) == 'metadata.json':
                    metadata_ti = tf.getmember(fname)
                    break

            if metadata_ti is None:
                raise Exception("Can't find metadata.json for release: %s" %
                                self)

            metadata = tf.extractfile(metadata_ti.name).read()

        for encoding in ('utf-8', 'latin-1'):
            try:
                return metadata.decode(encoding)
            except UnicodeDecodeError:
                continue

        raise Exception("Can't find an encoding for metadata.json")

    @property
    def metadata(self):
        return json.loads(self.metadata_json)
