#! /usr/bin/env python
# -*- encoding: utf-8 -*-
 
from PyQt4.Qt import *

from ui_cfgsocket import Ui_SocketCfgDialog

class SocketCfgDialog(Ui_SocketCfgDialog, QDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

    def get_addr(self):
        addr = str(self.lineAddr.text())
        port = self.spinPort.value()
        return (addr, port)
    
    def get_timeout(self):
        return self.spinTimeOut.value()
    