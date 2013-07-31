# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import sys

class HexSpinBox(QtGui.QSpinBox):
    # http://www.qtforum.org/article/15059/qspinbox-in-hex.html
    def valueFromText(self, text):
        try:
            return int(text, 16)
        except ValueError:
            return 0

    def textFromValue(self, value):
        text = '%x' % value
        return text.upper()

    def validate(self, text, integer):
        if self.valueFromText(text):
            return QtGui.QValidator.Acceptable
        return QtGui.QValidator.Invalid


class QBitWidget(QtGui.QWidget):
    '''Widget that allows bit integer manipulation with
    bit/hex display'''
    def __init__(self, bits=16, bit_titles=None, compact=None):
        QtGui.QWidget.__init__(self)
        self.bits = bits
        self.update_lock = False
        self.setupUi()

        for chbox, title in zip(self.checkboxes, bit_titles or []):
            chbox.setToolTip(title)

    def createCheckboxesLayout(self):
        self.checkboxes = []
        checkboxes_layout = QtGui.QHBoxLayout()
        checkboxes_layout.setSpacing(0)
        checkboxes_layout.setMargin(0)
        for i in range(self.bits):
            checkbox = QtGui.QCheckBox()
            checkboxes_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
        self.checkboxes.reverse()
        for n, chbox in enumerate(self.checkboxes):
            chbox.index = n
            chbox.stateChanged.connect(self.checkbox_clicked)
        return checkboxes_layout

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        self.widgetCheckboxes = QtGui.QWidget()

        self.widgetCheckboxes.setLayout(self.createCheckboxesLayout())

        layout.addWidget(self.widgetCheckboxes)

        self.spinner = QtGui.QSpinBox()
        #self.spinner = HexSpinBox()

        self.spinner.setMinimum(0)
        self.spinner.setMaximum(2**self.bits -1)
        self.spinner.valueChanged.connect(self.spinBox_valueChanged)
        self.spinner.value
        bottom = QtGui.QHBoxLayout()
        self.hex_label = QtGui.QLabel('0')
        bottom.addWidget(self.hex_label)
        bottom.addWidget(self.spinner)
        layout.addLayout(bottom)
        self.setLayout(layout)

    def spinBox_valueChanged(self, value):
        # Update Hex Representation

        hex_string = ('{0:04x}'.format(value)).upper()
        self.hex_label.setText(hex_string)

        if self.update_lock:
            return
        # Clean
        for chbox in self.checkboxes:
            chbox.setCheckState(QtCore.Qt.Unchecked)
        # Set bits
        bitrepr = '{0:b}'.format(value)[::-1]
        for n, state in enumerate(bitrepr):
            if state == '1':
                checkbox = self.checkboxes[n]
                checkbox.setCheckState(QtCore.Qt.Checked)

    def checkbox_clicked(self, state):
        value = 0
        for chbox in self.checkboxes:
            if chbox.isChecked():
                value += 2 ** chbox.index

        self.update_lock = True
        self.spinner.setValue(value)
        self.update_lock = False

    @property
    def value(self):
        return self.spinner.value()

    @value.setter
    def value(self, value):
        self.spinner.setValue(value)

    def add_bit_event(self, bit, callable, state=None):
        raise NotImplementedError("Does not support this feature yet")

class BitBlockWidget(QtGui.QWidget):
    '''A bit block'''
    def __init__(self, title=None, width=16, count=1):
        QtGui.QWidget.__init__(self)
        self.title = title
        self.width = width
        self.count = count
        self.bit_widgets = []
        self.setupUi()


    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        widget = QtGui.QGroupBox()
        widget.setTitle(self.title)
        widget_layout = QtGui.QVBoxLayout()
        widget.setLayout(widget_layout)
        for i in range(self.count):
            inner_widget = self.createWidget()
            self.bit_widgets.append(inner_widget)
            widget_layout.addWidget(inner_widget)
        layout.addWidget(widget)
        self.setLayout(layout)

    def createWidget(self):
        return QBitWidget(bits=self.width, )

    def __getitem__(self, index):
        return self.bit_widgets[index]

    def add_bit_event(self, word, bit, callable, state=None):
        '''Cretes a bit change observer'''
        self[word].add_bit_event(bit=bit, callable=callable, state=state)

class QAnalogWidget(QtGui.QWidget):
    def __init__(self, bits=14, tooltip=None):
        QtGui.QWidget.__init__(self)
        self.bits = bits
        if tooltip:
            self.setToolTip(tooltip)
        self.setupUi()

    def setupUi(self):
        layout = QtGui.QHBoxLayout()
        self.checkbox = QtGui.QCheckBox()
        layout.addWidget(self.checkbox)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)

        self.slider.setMinimum(0)
        self.slider.setMaximum(2**self.bits)

        layout.addWidget(self.slider)
        #layout.addWidget()
        self.setLayout(layout)

    @property
    def value(self):
        return self.slider.value()

    @value.setter
    def value(self, new):
        self.slider.setValue(new)

class AnalogBlockWidget(QtGui.QWidget):
    def __init__(self, title, width=14, count=1):
        QtGui.QWidget.__init__(self)
        self.title = title
        self.width = width
        self.count = count
        self.widgets = []
        self.setupUi()

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        for i in range(self.count):
            widget = self.createWidget()
            self.widgets.append(widget)
            layout.addWidget(widget)
        self.setLayout(layout)

    def createWidget(self):
        return QAnalogWidget(bits=self.width, tooltip = 'AAA')

    def __getitem__(self, index):
        return self.widgets[index]

class Simulator(QtGui.QWidget):
    _ais = None
    _dis = None
    _svs = None

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi()

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        layout_buttons = QtGui.QHBoxLayout()
        layout_buttons.addSpacing(1)
        layout_buttons.addWidget(QtGui.QPushButton("Read DB"))
        layout_buttons.addWidget(QtGui.QPushButton("Random!"))
        layout.addLayout(layout_buttons)

        layout_controls = QtGui.QHBoxLayout()
        self.createControls()
        layout_controls.addWidget(self.svs)
        layout_controls.addWidget(self.dis)
        layout_controls.addWidget(self.ais)
        layout.addLayout(layout_controls)
        self.setLayout(layout)

    def createControls(self):
        self.createSVS()
        self.createDIS()
        self.createAIS()

    def createSVS(self):
        self._svs = BitBlockWidget(title='VarSys', width=16, count=12)

    def createDIS(self):
        self._dis = BitBlockWidget(title='DIs', width=16, count=6)

    def createAIS(self):
        self._ais = AnalogBlockWidget(title='AI', count=10)

    @property
    def svs(self):
        return self._svs

    @property
    def dis(self):
        return self._dis

    @property
    def ais(self):
        return self._ais

def main():
    from random import randint, seed
    from os import getpid
    seed(getpid())

    def titulos(cant=16):
        for i in range(cant):
            yield 'Bit N#%d' % i

    app = QtGui.QApplication(sys.argv)
    #win = BitBlockWidget(title='DIs', width=16, count=6)
    win = Simulator()

    win.setWindowTitle("Simulación de un COMaster")
    #win = QBitWidget(8)
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
