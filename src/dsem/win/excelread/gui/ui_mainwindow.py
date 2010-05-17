# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/ui_files/mainwindow.ui'
#
# Created: Sun Nov  9 03:34:19 2008
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 191)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/res/wizard.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setPixmap(QtGui.QPixmap(":/icons/res/convert.png"))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 3)
        self.lineXLSPath = QtGui.QLineEdit(Form)
        self.lineXLSPath.setObjectName("lineXLSPath")
        self.gridLayout.addWidget(self.lineXLSPath, 0, 1, 1, 2)
        self.pushFileDialog = QtGui.QPushButton(Form)
        self.pushFileDialog.setMinimumSize(QtCore.QSize(0, 24))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/res/find.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushFileDialog.setIcon(icon1)
        self.pushFileDialog.setIconSize(QtCore.QSize(24, 24))
        self.pushFileDialog.setObjectName("pushFileDialog")
        self.gridLayout.addWidget(self.pushFileDialog, 1, 0, 1, 1)
        self.pushOK = QtGui.QPushButton(Form)
        self.pushOK.setMinimumSize(QtCore.QSize(0, 24))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/res/endturn.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushOK.setIcon(icon2)
        self.pushOK.setIconSize(QtCore.QSize(24, 24))
        self.pushOK.setObjectName("pushOK")
        self.gridLayout.addWidget(self.pushOK, 1, 1, 1, 1)
        self.pushSalir = QtGui.QPushButton(Form)
        self.pushSalir.setMinimumSize(QtCore.QSize(0, 24))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/res/exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushSalir.setIcon(icon3)
        self.pushSalir.setIconSize(QtCore.QSize(24, 24))
        self.pushSalir.setObjectName("pushSalir")
        self.gridLayout.addWidget(self.pushSalir, 1, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.pushSalir, QtCore.SIGNAL("clicked()"), Form.close)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Planilla:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushFileDialog.setText(QtGui.QApplication.translate("Form", "Buscar", None, QtGui.QApplication.UnicodeUTF8))
        self.pushOK.setText(QtGui.QApplication.translate("Form", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.pushSalir.setText(QtGui.QApplication.translate("Form", "Salir", None, QtGui.QApplication.UnicodeUTF8))

import data_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

