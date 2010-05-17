#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt4.Qt import *

class HexSpinBox(QSpinBox):
    def __init__(self, *largs):
        QSpinBox.__init__(self, *largs)
        self.setRange(0x00, 0xFFFF)
        self.validator = QRegExpValidator(QRegExp(r'[0-9A-Fa-f]{1,8}'), self)
    
    def validate(self, text, pos):
        return self.validator.validate(text, pos)
    
    def textFromValue(self, val):
        return ('%.2x' % val).upper()
    
    def valueFromText(self, text):
        text = str(text) # QString -> str
        return int(text, 16)
    
    def mapValueToText(self, i):
        print "Mapeando i", i
        return ("%.x" % i).upper()