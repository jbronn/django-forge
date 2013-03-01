import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class ForgeStorage(FileSystemStorage):

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        # Clobber existing files, or else will get filenames that won't
        # comply with the module naming format.
        if self.exists(name):
            self.delete(name)
        return name
