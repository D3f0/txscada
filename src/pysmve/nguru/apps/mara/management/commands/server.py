try:
    from .gui import EmulatorWindow
    GUI_AVALIABLE = True
except ImportError:
    GUI_AVALIABLE = False
import sys
from django.core.management.base import NoArgsCommand, CommandError
from optparse import make_option
from protocols import constants, mara
from twisted.internet import reactor

class Command(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('-p', '--port',
                    default=constants.DEFAULT_COMASTER_PORT,
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
            return self.buildGui()

        port = options.get('port')
        print "Iniciando el emulador de CoMaster en el puerto %s" % port
        reactor.listenTCP(port, mara.server.MaraServerFactory())
        reactor.run()

    def buildGui(self):
        if not GUI_AVALIABLE:
            raise CommandError("Qt not available (virtualenv?)")
        EmulatorWindow.launch()

