#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from pyscada.gui.ui_logwin import Ui_LogWinForm

from PyQt4 import QtGui, QtCore

class LogWin(QtGui.QWidget, Ui_LogWinForm):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

    def hideEvent(self, *args, **kwrgs):
        self.emit(QtCore.SIGNAL('hidden()'))
    
    def add_log(self, line):
        self.textEdit.append(line[:-1])