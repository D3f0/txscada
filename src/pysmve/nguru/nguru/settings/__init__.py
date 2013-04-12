# Monkey patch local path
import sys

from base import *
if DEBUG:
    sys.path.append(join(PROJECT_ROOT, '..', '..', '..'))
from zmq import *
from websockets import *
# Django query by example
from qbe import *

try:
    from local_settings import *
except ImportError:
    pass
