from PyQt4 import QtCore, QtGui


class DigitalSpinner(QtGui.QWidget):


    def __init__(self, bits=8, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        if bits < 1 or bits > 32:
            raise ValueError("DigitalSpinner soporta de 1 a 32 btis de longitud")
        self.bits = bits
        self.setWindowTitle("DigitalSpinner")
        self.updatingCheckboxes = False
        self.setupUi()


    def setupUi(self):
        main_layout = QtGui.QVBoxLayout()
        sub_layout = QtGui.QHBoxLayout()
        self.spinner = QtGui.QSpinBox()
        #self.spinner.editor().setAlignment(QtCore.Qt.AlignRight)
        self.spinner.valueChanged.connect(self.spinerValueChanged)
        self.spinner.setMaximum(2**self.bits)
        sub_layout.addSpacing(0)

        sub_layout.addWidget(self.spinner)
        sub_layout.addSpacing(0)
        main_layout.addLayout(sub_layout)
        bits_layout = QtGui.QHBoxLayout()
        bits_layout.setSpacing(0)

        self.createCheckboxes()
        for checkbox in reversed(self.checkboxes):
            bits_layout.addWidget(checkbox)
        main_layout.addLayout(bits_layout)

        self.setLayout(main_layout)

    def createCheckboxes(self):
        self.checkboxes = []
        for i in range(self.bits):
            checkbox = QtGui.QCheckBox()
            checkbox.value = 2 ** i
            checkbox.toggled.connect(self.checbkox_toggled)
            checkbox.setToolTip("%d" % checkbox.value)
            self.checkboxes.append(checkbox)

    def checbkox_toggled(self, checked):
        self.spinner.setValue(self.valueFromCheckboxes())

    def updateCheckboxesWithValue(self, value):
        self.updatingCheckboxes = True
        for i in range(self.bits):
            v = 2 ** i
            check = value & v == 1
            self.checkboxes[i].setChecked(check)
        self.updatingCheckboxes = False

    def spinerValueChanged(self, value):

        if not self.updatingCheckboxes:
            self.updateCheckboxesWithValue(value)


    def valueFromCheckboxes(self):
        value = sum([ c.value for c in self.checkboxes if c.isChecked()])
        return value

def test():
    import sys
    app = QtGui.QApplication(sys.argv)
    win = DigitalSpinner()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
