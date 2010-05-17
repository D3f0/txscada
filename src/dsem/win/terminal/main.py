#! /usr/bin/env python
# -*- encoding: utf-8 -*-
 
import os
import sys

if os.path.dirname(__file__) and os.getcwd() != os.path.dirname(__file__):
    # Correcion de directorio donde se ejecuta el interprete
    # para permitir cargar las imagenes de la GUI.
    os.chdir(os.path.dirname(__file__))

# Para poder imoportar Paquete metemos en el path...
sys.path.append( os.path.sep.join(('..', '..',)) )

# Fin del manejo de paths...
from PyQt4 import QtGui
from gui.mainwin import MainWin

def main(argv = sys.argv):
    app = QtGui.QApplication(argv)
    win = MainWin()
    win.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
