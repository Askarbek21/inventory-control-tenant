import os
from decouple import config

DJANGO_ENV = config('DJANGO_ENV', default='local')

if DJANGO_ENV == 'local':
    from .local import *
else:
    from .production import *
