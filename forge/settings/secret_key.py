"""
Functions for generating SECRET_KEY setting file.
"""

def secret_key(length=50):
    from django.utils.crypto import get_random_string
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(length, chars)


def secret_key_file(settings_file):
    with open(settings_file, 'w') as fh:
        fh.write("SECRET_KEY = '%s'\n" % secret_key())
