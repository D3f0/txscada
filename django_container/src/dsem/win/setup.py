#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from distutils.core import setup

import os, sys, re
sys.path.insert(0,os.path.abspath('..'))

from setup_utils import recursive_datadir_list, recursive_module_list, mkpath,\
                        recurive_module_sub_dir



try:
    import py2exe
except ImportError:
    if sys.platform.startswith('linux'):
        pass
    else:
        raise
    
UNDESIRED_PATTERNS = (
    r'README',
)


DATA_DIRS = recursive_datadir_list(mkpath('winlauncher', 'res'), UNDESIRED_PATTERNS, 1) 
DATA_DIRS += recursive_datadir_list(mkpath('..','dscada', 'templates'), UNDESIRED_PATTERNS, 2)
DATA_DIRS += recursive_datadir_list(mkpath('..','dscada', 'public'), UNDESIRED_PATTERNS, 2)
DATA_DIRS += recursive_datadir_list(mkpath('..','dscada', 'db'), UNDESIRED_PATTERNS, 2)

# Agregar Templates de Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'dscada.settings'
from dscada import settings 
DATA_DIRS += recurive_module_sub_dir(settings.INSTALLED_APPS, 'templates')
DATA_DIRS += recurive_module_sub_dir('django.contrib.admin', 'media')
# Test
DATA_DIRS += recurive_module_sub_dir('django', 'conf')
DATA_DIRS += recurive_module_sub_dir('django', os.path.join('contrib', 'admin'))

if 'linux' in sys.platform:
    from pprint import pprint
    pprint(DATA_DIRS)
    sys.exit()

includes = ['sip']
includes += recursive_module_list('winlauncher')
includes += recursive_module_list('cherrypy', full_search = True)
includes += recursive_module_list('dscada', full_search = True)
includes += ['server']
includes += recursive_module_list('django', full_search = True)
includes += [ 
       'email.mime.audio',  
       'email.mime.base',  
       'email.mime.image',  
       'email.mime.message',  
       'email.mime.multipart',  
       'email.mime.nonmultipart',  
       'email.mime.text',  
       'email.charset',  
       'email.encoders',  
       'email.errors',  
       'email.feedparser',  
       'email.generator',  
       'email.header',  
       'email.iterators',  
       'email.message',  
       'email.parser',  
       'email.utils',  
       'email.base64mime',  
       'email.quoprimime',
]
    
#includes += recursive_module_list('dscada')


options = {
           "py2exe": { "includes": includes,
                       "excludes": ['Tkinter',],
                        "compressed":1, 
                        "optimize":2,
                        "dist_dir": "win32",
                        'ascii': 1,  
                        'bundle_files': 1,  
                        #'dist_dir': 'setup',  
                        'packages': [ 'encodings' ],  
                        'excludes' : [  
                            'pywin',  
                            'pywin.debugger',  
                            'pywin.debugger.dbgcon',  
                            'pywin.dialogs',  
                            'pywin.dialogs.list',  
                            'Tkconstants',  
                            'Tkinter',  
                            'tcl',  
                        ],  

                        }
           }

setup( console=[{
                "script":"winlauncher/main.py",
                "icon_resources": [(1, "winlauncher/res/ico/icon.ico")],
                }
        ], 
        options=options,
        data_files = DATA_DIRS,
)
