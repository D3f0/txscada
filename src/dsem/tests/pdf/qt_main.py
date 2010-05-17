import sys
from PyQt4 import QtCore, QtGui
import ho.pisa as pisa
import cStringIO as StringIO

class MyWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setup_ui()
        self.setWindowTitle('Pruebas de Pisa + Jinja 2 + Qt')
        QtCore.QMetaObject.connectSlotsByName(self)


    def setup_ui(self):
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(QtGui.QLabel(u"""
        <h3>Prueba de Jinja2 + Pisa</h3>"""))
        self.button1 = QtGui.QPushButton('Hello')
        self.button1.setObjectName('button1')
        layout.addWidget(self.button1)
        self.setLayout(layout)
    
    def on_button1_pressed(self):
        QtGui.QMessageBox.information(None, "Hola", "Hola")
        
def main(argv = sys.argv):
    app = QtGui.QApplication(argv)
    win = MyWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    sys.exit(main())
 
