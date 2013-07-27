

import sys
from django.core.management.base import NoArgsCommand, CommandError
from optparse import make_option


class Command(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('-p', '--port',
                    default=9761,
                    help='TCP Port',
                    ),
        make_option('-g', '--gui',
                    default=False,
                    help="Show COMaster Emulator GUI",
                    action='store_true',
                    ),
    )

    help = 'Runs an COMaster emulator'

    def handle_noargs(self, **options):
        if options.get('gui'):
            self.buildGui()
        port = options.get('port')
        from twisted.internet import reactor
        from protocols import mara
        print "Iniciando el emulador de CoMaster en el puerto %s" % port
        reactor.listenTCP(port, mara.server.MaraServerFactory())
        reactor.run()

    def buildGui(self):
        from PyQt4 import QtCore, QtGui
        import qt4reactor
        app = QtGui.QApplication(sys.argv)
        qt4reactor.install()
        from .gui import EmulatorWindow
        self.window = EmulatorWindow()
        self.window.show()
