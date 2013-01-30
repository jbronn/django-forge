import os
import re
import tarfile

from django.conf import settings
from django.db import models
from django.utils import simplejson

from forge.constants import MODULE_REGEX


class Author(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __unicode__(self):
        return self.name


class Module(models.Model):
    author = models.ForeignKey(Author)
    name = models.CharField(max_length=128, db_index=True)
    desc = models.TextField(db_index=True, blank=True)
    tags = models.TextField(db_index=True, blank=True)

    class Meta:
        unique_together = ('author', 'name')

    def __unicode__(self):
        return u'%s/%s' % (self.author, self.name)

    @classmethod
    def parse_full_name(cls, full_name):
        match = MODULE_REGEX.match(full_name)
        if match:
            return (match.group('author'), match.group('module'))
        else:
            return None

    @classmethod
    def get_for_full_name(cls, full_name):
        parsed = Module.parse_full_name(full_name)
        if parsed:
            author, name = parsed
            return Module.objects.get(author__name=author, name=name)
        else:
            raise Module.DoesNotExist

    @property
    def tag_list(self):
        return self.tags.split()


def tarball_upload(instance, filename):
    author = instance.module.author.name
    return '/'.join([author[0].lower(), author, filename])


class Release(models.Model):
    module = models.ForeignKey(Module)
    version = models.CharField(max_length=128, db_index=True)
    tarball = models.FileField(upload_to=tarball_upload)

    class Meta:
        unique_together = ('module', 'version')

    def __unicode__(self):
        return u'%s version %s' % (self.module, self.version)

    @property
    def metadata_json(self):
        with tarfile.open(self.tarball.path, mode='r:gz') as tf:
            metadata_ti = None
            for fname in tf.getnames():
                if os.path.basename(fname) == 'metadata.json':
                    metadata_ti = tf.getmember(fname)
                    break

            if metadata_ti is None:
                raise Exception("Can't find metadata.json for release: %s" % self)

            metadata = tf.extractfile(metadata_ti.name).read()

        return metadata

    @property
    def metadata(self):
        return simplejson.loads(self.metadata_json)
