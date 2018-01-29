#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
from os import getcwd
from os.path import join, sep
sys.path.append(join(getcwd(), '..', '..'))
from distutils.core import setup
try:
    import py2exe
except ImportError:
    # Si llega a dar un error de importerror es porque no estamos en windows
    sys.stderr.write("Estamos en windows?")
    sys.exit(2)

setup(windows=[{"script" : "main.py",
                "icon_resources": [
                                   (1, "gui/ui_files/res/icon.ico")
                                   ],
                }
                ], 
      options={"py2exe" : {"includes" : 
                           [
                            # PyQt
                            "sip",
                            # Librerías
                            "xlrd",
                            #
                            "lib.xls_file",
                            ]
                           }
      })

