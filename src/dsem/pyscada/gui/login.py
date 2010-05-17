'''
Created on 15/04/2009

@author: defo
'''
from pyscada.gui.ui_login import Ui_Dialog
from PyQt4.QtGui import QDialog

class DialogLogin(QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
    
    def accept(self):
        if self.line_password.text() not in ['admin', 'oper']:
            return
        QDialog.accept(self)
        
