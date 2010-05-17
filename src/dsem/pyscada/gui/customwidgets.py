#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class QPushBtnEnabler(QPushButton):
    '''
    This button emits a signal when it's enabled.
    '''
    def setEnabled(self, enabled):
        self.emit(SIGNAL('enabled(bool)'), enabled)
        QPushButton.setEnabled(self, not enabled)


#===============================================================================
# QLogger
#===============================================================================
class QLogger(QObject):
    ''' File like object '''
    def __init__(self):
        ''' Constructor '''
        QObject.__init__(self)
        self.buffer = ''

    def write(self, data):
        ''' Escritura en el archivo '''
        self.buffer = u'%s%s' % (self.buffer, data)
    
    def flush(self):
        ''' Envio de los datos '''
        self.emit(SIGNAL('flush(QString)'), self.buffer[:-1])
        self.buffer = ''