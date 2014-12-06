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
from testing import *

try:
    from local_settings import *
except ImportError:
    pass
