# Monkey patch local path
import sys
import os
from base import *
# This is made so Django project is able to be used from upper immediate 
# directory structure
# TODO: Chek if this hack is still necessary
_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(os.path.join(_path, 'nguru'))
sys.path.append(os.path.join(_path, 'nguru/nguru'))

# Basic settings
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': os.environ.get('DB_NAME', 'travisdb'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}
