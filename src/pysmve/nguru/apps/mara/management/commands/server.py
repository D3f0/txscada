from django.core.management.base import NoArgsCommand
from optparse import make_option
from protocols import constants, mara
from twisted.internet import reactor


class Command(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('-p', '--port',
                    default=constants.DEFAULT_COMASTER_PORT,
                    help='TCP Port',
                    ),

    )

    help = 'Runs an COMaster emulator'

    def handle_noargs(self, **options):
        port = options.get('port')
        print "Iniciando el emulador de CoMaster en el puerto %s" % port
        reactor.listenTCP(port, mara.server.MaraServerFactory())
        reactor.run()
