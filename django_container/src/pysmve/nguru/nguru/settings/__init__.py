# Monkey patch local path
import sys
from os.path import abspath, join, dirname

# This is made so Django project is able to be used from upper immediate directory
# structure
_path = abspath(join(dirname(__file__), '../../..'))
sys.path.append(join(_path, 'nguru'))
sys.path.append(join(_path, 'nguru/nguru'))

# Basic settings
from base import *
#if DEBUG:
#    sys.path.append(join(PROJECT_ROOT, '..', '..', '..'))
from zmq import *
from websockets import *
# Django query by example
from qbe import *
# Redis
from redis import *
from testing import *

try:
    from local_settings import *
except ImportError:
    pass

if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql_psycopg2',
            'NAME':     'travisdb',
            'USER':     'postgres',
            'PASSWORD': '',
            'HOST':     'localhost',
            'PORT':     '',
        }
    }
