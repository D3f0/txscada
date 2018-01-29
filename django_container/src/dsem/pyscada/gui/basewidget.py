#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt4 import QtGui, QtCore

class QBaseWidget(QtGui.QWidget):

    def closeEvent(self, event):
        self.emit(QtCore.SIGNAL('closed()'))
