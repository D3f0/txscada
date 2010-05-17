# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/ui_files/logwin.ui'
#
# Created: Mon Nov 24 18:59:52 2008
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_LogWinForm(object):
    def setupUi(self, LogWinForm):
        LogWinForm.setObjectName("LogWinForm")
        LogWinForm.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(LogWinForm)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(LogWinForm)
        self.label.setEnabled(False)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(LogWinForm)
        self.comboBox.setEnabled(False)
        self.comboBox.setEditable(True)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 2)
        self.textEdit = QtGui.QTextEdit(LogWinForm)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 1, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(283, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 2)
        self.pushButton = QtGui.QPushButton(LogWinForm)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 2, 2, 1, 1)

        self.retranslateUi(LogWinForm)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), self.textEdit.clear)
        QtCore.QMetaObject.connectSlotsByName(LogWinForm)

    def retranslateUi(self, LogWinForm):
        LogWinForm.setWindowTitle(QtGui.QApplication.translate("LogWinForm", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LogWinForm", "Filtrar:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("LogWinForm", "Limpiar", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    LogWinForm = QtGui.QWidget()
    ui = Ui_LogWinForm()
    ui.setupUi(LogWinForm)
    LogWinForm.show()
    sys.exit(app.exec_())

