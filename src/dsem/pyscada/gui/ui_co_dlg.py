# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/ui_files/co_dlg.ui'
#
# Created: Wed Jan 28 04:42:24 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DialogCO(object):
    def setupUi(self, DialogCO):
        DialogCO.setObjectName("DialogCO")
        DialogCO.resize(400, 394)
        self.verticalLayout = QtGui.QVBoxLayout(DialogCO)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(DialogCO)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.spinNum = QtGui.QSpinBox(DialogCO)
        self.spinNum.setMinimum(0)
        self.spinNum.setMaximum(63)
        self.spinNum.setObjectName("spinNum")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.spinNum)
        self.label_2 = QtGui.QLabel(DialogCO)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.lineAddress = QtGui.QLineEdit(DialogCO)
        self.lineAddress.setObjectName("lineAddress")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineAddress)
        self.label_3 = QtGui.QLabel(DialogCO)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.spinNum_2 = QtGui.QSpinBox(DialogCO)
        self.spinNum_2.setMinimum(0)
        self.spinNum_2.setMaximum(63)
        self.spinNum_2.setObjectName("spinNum_2")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.spinNum_2)
        self.label_4 = QtGui.QLabel(DialogCO)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.spinNum_3 = QtGui.QSpinBox(DialogCO)
        self.spinNum_3.setMinimum(0)
        self.spinNum_3.setMaximum(63)
        self.spinNum_3.setObjectName("spinNum_3")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.spinNum_3)
        self.label_5 = QtGui.QLabel(DialogCO)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_5)
        self.spinNum_4 = QtGui.QSpinBox(DialogCO)
        self.spinNum_4.setMinimum(0)
        self.spinNum_4.setMaximum(63)
        self.spinNum_4.setObjectName("spinNum_4")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.spinNum_4)
        self.label_6 = QtGui.QLabel(DialogCO)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label_6)
        self.spinNum_5 = QtGui.QSpinBox(DialogCO)
        self.spinNum_5.setMinimum(0)
        self.spinNum_5.setMaximum(63)
        self.spinNum_5.setObjectName("spinNum_5")
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.spinNum_5)
        self.label_7 = QtGui.QLabel(DialogCO)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.label_7)
        self.comboBox = QtGui.QComboBox(DialogCO)
        self.comboBox.setObjectName("comboBox")
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.comboBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.checkBox = QtGui.QCheckBox(DialogCO)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)
        self.buttonBox = QtGui.QDialogButtonBox(DialogCO)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DialogCO)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), DialogCO.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), DialogCO.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogCO)

    def retranslateUi(self, DialogCO):
        DialogCO.setWindowTitle(QtGui.QApplication.translate("DialogCO", "Concentrador", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DialogCO", "Número de concentrador", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("DialogCO", "Dirección IP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("DialogCO", "Tiempo de poll", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("DialogCO", "Timeout", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("DialogCO", "Número de reintentos", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("DialogCO", "Retardo interconsulta", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("DialogCO", "Nombre:", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("DialogCO", "Habilitado", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DialogCO = QtGui.QDialog()
    ui = Ui_DialogCO()
    ui.setupUi(DialogCO)
    DialogCO.show()
    sys.exit(app.exec_())

