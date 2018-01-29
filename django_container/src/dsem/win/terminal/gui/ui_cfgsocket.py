# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/defo/Documentos/Universidad/Picnet/src/dsem/win/terminal/gui/ui_files/cfgsocket.ui'
#
# Created: Sun Oct 19 01:56:51 2008
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SocketCfgDialog(object):
    def setupUi(self, SocketCfgDialog):
        SocketCfgDialog.setObjectName("SocketCfgDialog")
        SocketCfgDialog.resize(276, 137)
        SocketCfgDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(SocketCfgDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(SocketCfgDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineAddr = QtGui.QLineEdit(SocketCfgDialog)
        self.lineAddr.setObjectName("lineAddr")
        self.gridLayout.addWidget(self.lineAddr, 0, 1, 1, 2)
        self.label_2 = QtGui.QLabel(SocketCfgDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.spinPort = QtGui.QSpinBox(SocketCfgDialog)
        self.spinPort.setMinimum(1)
        self.spinPort.setMaximum(65536)
        self.spinPort.setProperty("value", QtCore.QVariant(9761))
        self.spinPort.setObjectName("spinPort")
        self.gridLayout.addWidget(self.spinPort, 1, 1, 1, 2)
        self.label_3 = QtGui.QLabel(SocketCfgDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 2)
        self.spinTimeOut = QtGui.QDoubleSpinBox(SocketCfgDialog)
        self.spinTimeOut.setDecimals(2)
        self.spinTimeOut.setMinimum(0.01)
        self.spinTimeOut.setSingleStep(0.1)
        self.spinTimeOut.setProperty("value", QtCore.QVariant(0.04))
        self.spinTimeOut.setObjectName("spinTimeOut")
        self.gridLayout.addWidget(self.spinTimeOut, 2, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(SocketCfgDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SocketCfgDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), SocketCfgDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), SocketCfgDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SocketCfgDialog)

    def retranslateUi(self, SocketCfgDialog):
        SocketCfgDialog.setWindowTitle(QtGui.QApplication.translate("SocketCfgDialog", "Configuración de Socket", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setToolTip(QtGui.QApplication.translate("SocketCfgDialog", "Dirección IP del destino.\n"
"Por defecto la placa MC WebDev tiene la direccion 192.168.1.8", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SocketCfgDialog", "Dirección", None, QtGui.QApplication.UnicodeUTF8))
        self.lineAddr.setText(QtGui.QApplication.translate("SocketCfgDialog", "192.168.1.8", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("SocketCfgDialog", "Puerto", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setToolTip(QtGui.QApplication.translate("SocketCfgDialog", "Tiempo de espera en el establecmiento del socket", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("SocketCfgDialog", "Timeout", None, QtGui.QApplication.UnicodeUTF8))
        self.spinTimeOut.setSuffix(QtGui.QApplication.translate("SocketCfgDialog", " segs.", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SocketCfgDialog = QtGui.QDialog()
    ui = Ui_SocketCfgDialog()
    ui.setupUi(SocketCfgDialog)
    SocketCfgDialog.show()
    sys.exit(app.exec_())

