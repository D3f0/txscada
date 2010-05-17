#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from ui_mainwin import Ui_MainWindow
from mapscene import MapScene

# Un alias
qapp = QtGui.QApplication.instance

class MainWin(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        # Seteamos la escena
        self.escena_mapa = MapScene()
        self.gvMapa.setScene(self.escena_mapa)
        #print qapp().path()
        
        
    def on_actionSalir_triggered(self):
        QtGui.QApplication.instance().exit()
        
    def hideEvent(self, event):
        ''' Lo recibe la QApplication'''
        self.emit(QtCore.SIGNAL('hidden()'))
        QtGui.QMainWindow.hideEvent(self, event)