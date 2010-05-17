#! /usr/bin/env python
# -*- encoding: utf-8 -*-
 

from PyQt4.Qt import *
from ui_about import Ui_Form

class AboutDialog(QDialog, Ui_Form):
    
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
if __name__ == "__main__":
    app = QApplication([])
    win = AboutDialog()
    win.show()
    app.exec_()