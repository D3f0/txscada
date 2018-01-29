# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/ui_files/wizard.ui'
#
# Created: Sat Feb 14 12:23:27 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_WizardDialog(object):
    def setupUi(self, WizardDialog):
        WizardDialog.setObjectName("WizardDialog")
        WizardDialog.resize(478, 300)
        self.verticalLayout = QtGui.QVBoxLayout(WizardDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtGui.QFrame(WizardDialog)
        self.frame.setFrameShape(QtGui.QFrame.HLine)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout.addWidget(self.frame)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushCancel = QtGui.QPushButton(WizardDialog)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/res/process-stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushCancel.setIcon(icon)
        self.pushCancel.setIconSize(QtCore.QSize(20, 20))
        self.pushCancel.setObjectName("pushCancel")
        self.horizontalLayout.addWidget(self.pushCancel)
        self.pushBack = QtGui.QPushButton(WizardDialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/res/go-previous.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushBack.setIcon(icon1)
        self.pushBack.setIconSize(QtCore.QSize(20, 20))
        self.pushBack.setObjectName("pushBack")
        self.horizontalLayout.addWidget(self.pushBack)
        self.pushNext = QtGui.QPushButton(WizardDialog)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/res/go-next.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushNext.setIcon(icon2)
        self.pushNext.setIconSize(QtCore.QSize(20, 20))
        self.pushNext.setObjectName("pushNext")
        self.horizontalLayout.addWidget(self.pushNext)
        self.pushFinish = QtGui.QPushButton(WizardDialog)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/res/dialog-ok-apply.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushFinish.setIcon(icon3)
        self.pushFinish.setIconSize(QtCore.QSize(20, 20))
        self.pushFinish.setObjectName("pushFinish")
        self.horizontalLayout.addWidget(self.pushFinish)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WizardDialog)
        QtCore.QObject.connect(self.pushCancel, QtCore.SIGNAL("clicked()"), WizardDialog.reject)
        QtCore.QObject.connect(self.pushFinish, QtCore.SIGNAL("clicked()"), WizardDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(WizardDialog)

    def retranslateUi(self, WizardDialog):
        WizardDialog.setWindowTitle(QtGui.QApplication.translate("WizardDialog", "Wizard", None, QtGui.QApplication.UnicodeUTF8))
        self.pushCancel.setText(QtGui.QApplication.translate("WizardDialog", "&Cancelar", None, QtGui.QApplication.UnicodeUTF8))
        self.pushBack.setText(QtGui.QApplication.translate("WizardDialog", "&Anterior", None, QtGui.QApplication.UnicodeUTF8))
        self.pushNext.setText(QtGui.QApplication.translate("WizardDialog", "&Siguiente", None, QtGui.QApplication.UnicodeUTF8))
        self.pushFinish.setText(QtGui.QApplication.translate("WizardDialog", "&Finalizar", None, QtGui.QApplication.UnicodeUTF8))

import data_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    WizardDialog = QtGui.QDialog()
    ui = Ui_WizardDialog()
    ui.setupUi(WizardDialog)
    WizardDialog.show()
    sys.exit(app.exec_())

