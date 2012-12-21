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
        reactor.listenTCP(options.get('port'), mara.server.MaraServerFactory())
        reactor.run()
