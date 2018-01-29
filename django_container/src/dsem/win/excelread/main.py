#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os

if "__file__" in globals():
    path = os.path.dirname(os.path.abspath(__file__))
elif "__path__" in globals():
    path = os.path.abspath(__path__)
else:
    path = os.getcwd()
# Agregamos al path a ../..
sys.path.append(os.path.join(path, '..', '..'))
    
from PyQt4 import QtGui

from gui.mainwindow import MainWindow

def main(argv = sys.argv):
    ''' Funcion main '''
    app = QtGui.QApplication(argv)
    win = MainWindow()
    win.show()
    return app.exec_()
    
    
if __name__ == "__main__":
    sys.exit(main())
