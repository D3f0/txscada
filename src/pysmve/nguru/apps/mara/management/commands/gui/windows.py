import sys
import qt4reactor
qt4reactor.install()
from twisted.internet import reactor
from PyQt4 import QtGui

class EmulatorWindow(QtGui.QWidget):

    def __init__(self):
        super(EmulatorWindow, self).__init__()
        self.setupUi()
        self.setWindowTitle("Emulator")

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        self.tabCOMasters = self.createTabWidgetCOMasters()
        layout.addWidget(self.tabCOMasters)
        self.setLayout(layout)


    def createTabWidgetCOMasters(self):
        tabs = QtGui.QTabWidget()
        for i in range(5):
            text = "COMaster %s" % i
            widget = self.createWidgetCOMaster()
            tabs.addTab(widget, text)
        return tabs


    def createWidgetCOMaster(self):
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QPushButton("Close"))
        widget.setLayout(layout)
        return widget

    @classmethod
    def launch(cls, obj=None):
        app = QtGui.QApplication(sys.argv)
        #import qt4reactor
        #qt4reactor.install()

        window = QtGui.QLabel("HOHO")
        window.show()
        print "Showing..."
        reactor.run()
