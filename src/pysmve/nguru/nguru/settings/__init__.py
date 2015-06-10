# Join all settings in one module
from base import *
from mara import *
from testing import *

try:
    from local_settings import *
except ImportError:
    pass

# WIP

try:
    from telegraphy import django
    INSTALLED_APPS += ('telegraphy.django.app', )
except ImportError:
    pass