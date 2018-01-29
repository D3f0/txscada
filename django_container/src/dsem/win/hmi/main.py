#! /usr/bin/env python
# -*- encoding: utf-8 -*-


#===============================================================================
# Imports para PyInstaller
#===============================================================================
import sip  
from PyQt4 import QtGui, QtCore

#===============================================================================
# Imports de la aplicación
#===============================================================================
from app import PySemControlApplication
import sys

def main(argv = sys.argv):
    ''' Funcion main '''
    app = PySemControlApplication(argv)
    return app.exec_()
    
if __name__ == "__main__":
    sys.exit(main())
