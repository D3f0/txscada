# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/defo/Documentos/Universidad/Picnet/src/dsem/win/terminal/gui/ui_files/cfgserial.ui'
#
# Created: Sun Oct 19 16:01:58 2008
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_CfgSerialDialog(object):
    def setupUi(self, CfgSerialDialog):
        CfgSerialDialog.setObjectName("CfgSerialDialog")
        CfgSerialDialog.resize(216, 317)
        self.gridLayout = QtGui.QGridLayout(CfgSerialDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(CfgSerialDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboPort = QtGui.QComboBox(CfgSerialDialog)
        self.comboPort.setObjectName("comboPort")
        self.gridLayout.addWidget(self.comboPort, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(CfgSerialDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.comboSpeed = QtGui.QComboBox(CfgSerialDialog)
        self.comboSpeed.setObjectName("comboSpeed")
        self.gridLayout.addWidget(self.comboSpeed, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(CfgSerialDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.comboSize = QtGui.QComboBox(CfgSerialDialog)
        self.comboSize.setObjectName("comboSize")
        self.gridLayout.addWidget(self.comboSize, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(CfgSerialDialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.comboParity = QtGui.QComboBox(CfgSerialDialog)
        self.comboParity.setObjectName("comboParity")
        self.gridLayout.addWidget(self.comboParity, 3, 1, 1, 1)
        self.label_5 = QtGui.QLabel(CfgSerialDialog)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.comboStop = QtGui.QComboBox(CfgSerialDialog)
        self.comboStop.setObjectName("comboStop")
        self.gridLayout.addWidget(self.comboStop, 4, 1, 1, 1)
        self.label_6 = QtGui.QLabel(CfgSerialDialog)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.comboXonXoff = QtGui.QComboBox(CfgSerialDialog)
        self.comboXonXoff.setObjectName("comboXonXoff")
        self.gridLayout.addWidget(self.comboXonXoff, 5, 1, 1, 1)
        self.label_7 = QtGui.QLabel(CfgSerialDialog)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.comboRtsCts = QtGui.QComboBox(CfgSerialDialog)
        self.comboRtsCts.setObjectName("comboRtsCts")
        self.gridLayout.addWidget(self.comboRtsCts, 6, 1, 1, 1)
        self.label_8 = QtGui.QLabel(CfgSerialDialog)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 7, 0, 1, 1)
        self.comboDsrDtr = QtGui.QComboBox(CfgSerialDialog)
        self.comboDsrDtr.setObjectName("comboDsrDtr")
        self.gridLayout.addWidget(self.comboDsrDtr, 7, 1, 1, 1)
        self.label_9 = QtGui.QLabel(CfgSerialDialog)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 8, 0, 1, 1)
        self.spinTimeOut = QtGui.QDoubleSpinBox(CfgSerialDialog)
        self.spinTimeOut.setMinimum(-1.0)
        self.spinTimeOut.setObjectName("spinTimeOut")
        self.gridLayout.addWidget(self.spinTimeOut, 8, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(CfgSerialDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)

        self.retranslateUi(CfgSerialDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), CfgSerialDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), CfgSerialDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CfgSerialDialog)

    def retranslateUi(self, CfgSerialDialog):
        CfgSerialDialog.setWindowTitle(QtGui.QApplication.translate("CfgSerialDialog", "Configuración Puerto Serial", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("CfgSerialDialog", "Dispositivo", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("CfgSerialDialog", "Velocidad", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("CfgSerialDialog", "Longitud de datos", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("CfgSerialDialog", "Paridad", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("CfgSerialDialog", "Bits de parada", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("CfgSerialDialog", "XonXoff", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("CfgSerialDialog", "RtsCts", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("CfgSerialDialog", "DsrDtr", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("CfgSerialDialog", "Timeout", None, QtGui.QApplication.UnicodeUTF8))
        self.spinTimeOut.setToolTip(QtGui.QApplication.translate("CfgSerialDialog", "Valores negativos hacen que no se tenga en cuenta el tiemeout.", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    CfgSerialDialog = QtGui.QDialog()
    ui = Ui_CfgSerialDialog()
    ui.setupUi(CfgSerialDialog)
    CfgSerialDialog.show()
    sys.exit(app.exec_())

