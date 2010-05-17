#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt4 import QtGui

from ui_mainwindow import Ui_Form
import os
from lib.xls_file import readexcel

class MainWindow(QtGui.QWidget, Ui_Form):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
    
    def on_pushFileDialog_pressed(self):
        path = QtGui.QFileDialog.getOpenFileName(self,
                                          u'Abrir planilla','',
                                          u'Archivos XLS (*.xls);;')
        self.lineXLSPath.setText(path)
        
    def on_pushOK_pressed(self):
        path = str(self.lineXLSPath.text())
        if not path:
            QtGui.QMessageBox.warning(self, "Sin path",
                                      "Busque un archivo")
            self.pushFileDialog.setFocus()
            
        elif not os.path.exists(path):
            QtGui.QMessageBox.warning(self, "El %s archivo no existe" % path,
                                      "No existe el archivo %s, compruebe la ruta" % path)
            self.lineXLSPath.setFocus()
        try:
            xls = readexcel(path)
        except Exception, e:
            QtGui.QMessageBox.information(self, "Error!", unicode(e))
        else:
            QtGui.QMessageBox.information(self, "Ok", u'Ok')
        
    
    
        
        