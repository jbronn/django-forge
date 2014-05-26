import os

# Not perfect, but prevents SECRET_KEY (generated the way Django does it)
# from being included in this repo and distributed to the world.  Contributes
# to a seamless "out of the box" experience.
settings_key = os.path.join(os.path.dirname(__file__), 'key.py')
if not os.path.isfile(settings_key):
    import random
    _sysrand = random.SystemRandom()
    _secret = ''.join(
        [_sysrand.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
         for i in range(50)])
    with open(settings_key, 'w') as fh:
        fh.write("SECRET_KEY = '%s'\n" % _secret)
from .key import SECRET_KEY
