#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from winlauncher.gui.ui_configwindow import Ui_Dialog
from PyQt4 import QtCore, QtGui
import os
from glob import glob
#print "OS.getcwd()", os.getcwd()

class ConfigDialog(QtGui.QDialog, Ui_Dialog):
    ''' Ventana de configuración '''
    
    def __init__(self, *args):
        # Constructor
        QtGui.QDialog.__init__(self, *args)
        # Iniciamos la GUI
        self.setupUi(self)
        self.adapt_ui_db_fields(self.comboBox_DB_type.currentIndex())
        self.load_config()
        
    def load_config(self, file = None):
        default_cfg = {
            'port' : '8000',
            'addr' : 'localhost',
            'db_ty': 0,
            'db_na': 'db/db.sqlite',
            'db_us': 'no aplica',
            'db_ps': 'no plica',
                       
        }
        configs = glob('config/*.yaml')
        
        if not file:
#            self.comboBox_DB_type. = 0
            self.lineEdit_addr.setText('127.0.0.1')
            self.lineEdit_port.setValue(8000)
            self.lineEdit_DB_user.setText('foo')
            self.lineEdit_DB_pass.setText('foo')
            self.lineEdit_DB_server.setText('localhost')
            self.lineEdit_DB_name.setText('no_db')
            self.update_link()
            
    def update_link(self):
        addr, port = self.lineEdit_addr.text(), self.lineEdit_port.value()
        url = 'http://%s:%s/' % (addr, port)
        if addr and port:
            self.label_link.setText('<a href="%s">%s<a>' % (url, url))
    
    def on_lineEdit_port_valueChanged(self, val):
        self.update_link()
    
    def on_lineEdit_addr_textChanged(self, text):
        self.update_link()
    
    
        
    @QtCore.pyqtSignature("int")
    def on_comboBox_DB_type_currentIndexChanged(self, index):
        self.adapt_ui_db_fields(index)
        
    def adapt_ui_db_fields(self, type):
        campos = [ 
                    self.label_DB_pass, self.label_DB_port, 
                    self.label_DB_server, self.label_DB_user,
                    self.lineEdit_DB_pass, self.lineEdit_DB_port, 
                    self.lineEdit_DB_server,self.lineEdit_DB_user,
                 ]
        if type == 0:
            # Es sqlite, no se utilizan ciertos campos...
            for x in campos:
                x.setEnabled(False)
        else:
            for x in campos:
                x.setEnabled(True)
                
#===============================================================================
#    Profiles
#===============================================================================
    @QtCore.pyqtSignature("")
    def on_pushButton_newprof_pressed(self):
        resp,ok = \
        QtGui.QInputDialog.getText(self,
                                   self.trUtf8("Nuevo perfil"),
                                   self.trUtf8("Ingrese el nomnbre del nuevo perfil"),
                                   QtGui.QLineEdit.Normal,
                                   "Nuevo perfil")
        if ok:
            print resp
            self.comboBox_profname.addItem(resp, QtCore.QVariant(len(resp)))
            
    @QtCore.pyqtSignature("")
    def on_pushButton_delprof_pressed(self):
        print "Delete"
                
    @QtCore.pyqtSignature("")
    def on_pushButton_loadprof_pressed(self):
        print "Load"
        
    @QtCore.pyqtSignature("")
    def on_pushButton_saveprof_pressed(self):
        print "Save"
