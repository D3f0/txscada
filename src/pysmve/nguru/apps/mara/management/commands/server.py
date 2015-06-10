

import sys
from django.core.management.base import NoArgsCommand, CommandError
from optparse import make_option
from apps.mara.models import Profile
from logging import getLogger, LoggerAdapter


class Command(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('-P', '--port',
                    default=9761,
                    help='TCP Port',
                    ),
        make_option('-g', '--gui',
                    default=False,
                    help="Show COMaster Emulator GUI",
                    action='store_true',
                    ),
        make_option('-p', '--profile',
                    default='default',
                    help="Database profile"),
    )

    help = 'Runs an COMaster emulator'

    def handle_noargs(self, **options):
        # Move arguments around with the command instance
        self.options = options
        profile_name = self.options['profile']
        try:
            self.profile = Profile.objects.get(name=profile_name)
        except Profile.DoesNotExist:
            raise CommandError("Profile %s does not exist" % profile_name)

        if self.options.get('gui'):
            self.runQtGui()
        else:
            port = options.get('port')
            from twisted.internet import reactor
            from protocols.mara import server
            server_factory = server.MaraServerFactory(logger=getLogger('commands'))
            reactor.listenTCP(port, server_factory)
            reactor.run()

    def runQtGui(self):
        import qt4reactor
        from PyQt4.QtGui import QApplication
        app = QApplication(sys.argv)
        qt4reactor.install()
        from .gui import SimulatorWidget
        win = SimulatorWidget()
        win.setWindowTitle("Simulador Profile: %s" % self.profile.name)
        win.add_di()
        win.show()
        return app.exec_()
