#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
from esquina import EsquinaGraphicsScene, EsquinaGraphicsView

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qt_dbhelp import dburl_to_qsqldb
from esquina_wizard import EsquinaConfigWizard
import os, sys
try:
    from pyscada.gui.wizard import ConfigWizard
except ImportError:
    sys.path += ('..', '..%s..' % os.sep)
    from pyscada.gui.wizard import ConfigWizard 

class EsquinaGrapConfigWizard(EsquinaConfigWizard):
    '''
    Wizard de configuracion de la esquina.
    A 
    '''
    def __init__(self, item):
        self.item = item
        EsquinaConfigWizard.__init__(self, None)
        self.steps.append(ConfiguracionCalles)
        self.steps.append(ConfiguracionSemaforos)
        self.create_widget()
        
        
class ConfiguracionCalles(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
#        layout = QVBoxLayout(self)
        layout = QGridLayout()
        layout.addWidget(QLabel("Configuracion calles para %s" %
                                str(self.parent())
                                , self))
        
        self.scene = EsquinaGraphicsScene() 
        self.esquinaConfigView = EsquinaGraphicsView(self.scene)
        
        layout.setRowMinimumHeight(1, 300)
        layout.setColumnMinimumWidth(0, 300)
        layout.addWidget(self.esquinaConfigView,1,0,5,2)
        layout.setRowStretch(1, 1)
        self.setLayout(layout)
#        self.parent().pushNext.setEnabled( True )
#   
    def show(self):
        self.scene.estado = EsquinaGraphicsScene.STATE_EDICION_CALLE
        QWidget.show(self)
     
class ConfiguracionSemaforos(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
#        layout = QVBoxLayout(self)
        layout = QGridLayout()
        layout.addWidget(QLabel("Configuracion calles para %s" %
                                str(self.parent())
                                , self))
        
        db = dburl_to_qsqldb('mysql://dsem:passmenot@localhost:3306/dsem')
        print db
    
#        iduc = parent.history[0].uc
        iduc = 0
        
        sqlmodel = QSqlQueryModel()
        
        sqlmodel.setQuery( QSqlQuery('SELECT can_movi FROM UC WHERE id = %'% iduc, db) )
        
        print "Error?", model.lastError().databaseText() or "Sim error :)"

        value = sqlmodel.record(0).value(0)
        print value
        
        self.model = QStandardItemModel(2,3)
        self.table = QTableView()
        self.table.setModel(self.model)
        layout.addWidget(self.table,1,0,2,3)
        
        self.scene = parent.history[parent.current_step - 1].scene
        self.scene.estado = EsquinaGraphicsScene.STATE_EDICION_SEMAFOROS 
        self.esquinaConfigView = EsquinaGraphicsView(self.scene)
        self.esquinaConfigView.setScene(self.scene)
        
        layout.setRowMinimumHeight(3, 300)
        layout.addWidget(self.esquinaConfigView,3,0,5,2)
#        layout.setRowStretch(3, 3)
        self.setLayout(layout)
    
    
if __name__ == '__main__':
    app = QApplication([])
    wiz = EsquinaGrapConfigWizard(app)
    wiz.show()
#    win = SeleccionUC(None)
    app.exec_()
















#
#
#
#
#class FirstPage(QtGui.QWidget):
#    def __init__(self, parent):
#        QtGui.QWidget.__init__(self, parent)
#
#        self.topLabel = QtGui.QLabel(self.tr("<center><b>Configurar la disposición de las calles</b></center>"
#                                             "<p>Armar la esquina de acuerdo a la disposición de las calles."))
#        self.topLabel.setWordWrap(False)
#    
#        self.nombreEsquinaLabel = QtGui.QLabel(self.tr("&Nombre de la esquina:"))
#        self.nombreEsquinaLineEdit = QtGui.QLineEdit()
#        self.nombreEsquinaLabel.setBuddy(self.nombreEsquinaLineEdit)
#        self.setFocusProxy(self.nombreEsquinaLineEdit)
#        
#        self.connect(self.nombreEsquinaLineEdit, QtCore.SIGNAL("textChanged(const QString &)"),
#                self.nombreEsquinaChanged)
#       
#        parent.setButtonEnabled(False)
#        
#        self.scene = EsquinaGraphicsScene() 
#        self.esquinaConfigView = EsquinaEditorCalleGraphicsView(self.scene)
#        
#        layout = QtGui.QGridLayout()
#        layout.addWidget(self.topLabel, 0, 0, 1, 2)
#        layout.setRowMinimumHeight(1, 10)
#        layout.addWidget(self.nombreEsquinaLabel, 2, 0)
#        layout.addWidget(self.nombreEsquinaLineEdit, 2, 1)
#        layout.setRowMinimumHeight(3, 300)
#        layout.addWidget(self.esquinaConfigView,3,0,5,2)
#        layout.setRowStretch(6, 1)
#        self.setLayout(layout)
#
#    def nombreEsquinaChanged(self):
#        wizard = self.parent()
#        wizard.setButtonEnabled(not self.nombreEsquinaLineEdit.text().isEmpty())
#
#        
#class SecondPage(QtGui.QWidget):
#    def __init__(self, parent):
#        QtGui.QWidget.__init__(self, parent)
#
#        self.topLabel = QtGui.QLabel(self.tr("<center><b>Code style options</b></center>"))
#    
#        self.commentCheckBox = QtGui.QCheckBox(self.tr("&Start generated files with a comment"))
#        self.commentCheckBox.setChecked(True)
#        self.setFocusProxy(self.commentCheckBox)
#    
#        self.protectCheckBox = QtGui.QCheckBox(self.tr("&Protect header file against "
#                                                       "multiple inclusions"))
#        self.protectCheckBox.setChecked(True)
#    
#        self.macroNameLabel = QtGui.QLabel(self.tr("&Macro name:"))
#        self.macroNameLineEdit = QtGui.QLineEdit()
#        self.macroNameLabel.setBuddy(self.macroNameLineEdit)
#    
#        self.includeBaseCheckBox = QtGui.QCheckBox(self.tr("&Include base class definition"))
#        self.baseIncludeLabel = QtGui.QLabel(self.tr("Base class include:"))
#        self.baseIncludeLineEdit = QtGui.QLineEdit()
#        self.baseIncludeLabel.setBuddy(self.baseIncludeLineEdit)
#    
#        className = QtCore.QString(parent.firstPage.classNameLineEdit.text())
#        self.macroNameLineEdit.setText(className.toUpper() + "_H")
#    
#        baseClass = QtCore.QString(parent.firstPage.baseClassLineEdit.text())
#        if baseClass.isEmpty():
#            self.includeBaseCheckBox.setEnabled(False)
#            self.baseIncludeLabel.setEnabled(False)
#            self.baseIncludeLineEdit.setEnabled(False)
#        else:
#            self.includeBaseCheckBox.setChecked(True)
#            if QtCore.QRegExp("Q[A-Z].*").exactMatch(baseClass):
#                self.baseIncludeLineEdit.setText("<" + baseClass + ">")
#            else:
#                self.baseIncludeLineEdit.setText("\"" + baseClass.toLower() + ".h\"")
#
#        self.connect(self.protectCheckBox, QtCore.SIGNAL("toggled(bool)"),
#                self.macroNameLabel, QtCore.SLOT("setEnabled(bool)"))
#        self.connect(self.protectCheckBox, QtCore.SIGNAL("toggled(bool)"),
#                self.macroNameLineEdit, QtCore.SLOT("setEnabled(bool)"))
#        self.connect(self.includeBaseCheckBox, QtCore.SIGNAL("toggled(bool)"),
#                self.baseIncludeLabel, QtCore.SLOT("setEnabled(bool)"))
#        self.connect(self.includeBaseCheckBox, QtCore.SIGNAL("toggled(bool)"),
#                self.baseIncludeLineEdit, QtCore.SLOT("setEnabled(bool)"))
#    
#        layout = QtGui.QGridLayout()
#        layout.setColumnMinimumWidth(0, 20)
#        layout.addWidget(self.topLabel, 0, 0, 1, 3)
#        layout.setRowMinimumHeight(1, 10)
#        layout.addWidget(self.commentCheckBox, 2, 0, 1, 3)
#        layout.addWidget(self.protectCheckBox, 3, 0, 1, 3)
#        layout.addWidget(self.macroNameLabel, 4, 1)
#        layout.addWidget(self.macroNameLineEdit, 4, 2)
#        layout.addWidget(self.includeBaseCheckBox, 5, 0, 1, 3)
#        layout.addWidget(self.baseIncludeLabel, 6, 1)
#        layout.addWidget(self.baseIncludeLineEdit, 6, 2)
#        layout.setRowStretch(7, 1)
#        self.setLayout(layout)
#
#        
#class ThirdPage(QtGui.QWidget):
#    def __init__(self, parent):
#        QtGui.QWidget.__init__(self, parent)
#        
#        self.topLabel = QtGui.QLabel(self.tr("<center><b>Output files</b></center>"))
#    
#        self.outputDirLabel = QtGui.QLabel(self.tr("&Output directory:"))
#        self.outputDirLineEdit = QtGui.QLineEdit()
#        self.outputDirLabel.setBuddy(self.outputDirLineEdit)
#        self.setFocusProxy(self.outputDirLineEdit)
#    
#        self.headerLabel = QtGui.QLabel(self.tr("&Header file name:"))
#        self.headerLineEdit = QtGui.QLineEdit()
#        self.headerLabel.setBuddy(self.headerLineEdit)
#    
#        self.implementationLabel = QtGui.QLabel(self.tr("&Implementation file name:"))
#        self.implementationLineEdit = QtGui.QLineEdit()
#        self.implementationLabel.setBuddy(self.implementationLineEdit)
#    
#        className = QtCore.QString(parent.firstPage.classNameLineEdit.text())
#        self.headerLineEdit.setText(className.toLower() + ".h")
#        self.implementationLineEdit.setText(className.toLower() + ".cpp")
#        self.outputDirLineEdit.setText(QtCore.QDir.convertSeparators(QtCore.QDir.homePath()))
#    
#        layout = QtGui.QGridLayout()
#        layout.addWidget(self.topLabel, 0, 0, 1, 2)
#        layout.setRowMinimumHeight(1, 10)
#        layout.addWidget(self.outputDirLabel, 2, 0)
#        layout.addWidget(self.outputDirLineEdit, 2, 1)
#        layout.addWidget(self.headerLabel, 3, 0)
#        layout.addWidget(self.headerLineEdit, 3, 1)
#        layout.addWidget(self.implementationLabel, 4, 0)
#        layout.addWidget(self.implementationLineEdit, 4, 1)
#        layout.setRowStretch(5, 1)
#        self.setLayout(layout)
#        
#
#if __name__ == '__main__':
#    app = QtGui.QApplication(sys.argv)
#    wizard = ClassWizard()
#    wizard.show()
#    sys.exit(wizard.exec_())
