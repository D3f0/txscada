from django.core.management.base import NoArgsCommand, CommandError
from twisted.internet import reactor
from optparse import make_option

class TwistedNoArgsCommand(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
            make_option('-n', '--no-run', help="Don't run reactor. Just setup, intended"
                " for testing", dest="dont_run_reactor", action="store_true",
                default=False),

        )

    def handle(self, *args, **options):
        if args:
            raise CommandError("Command doesn't accept any arguments")
        self.handle_noargs(**options)

        if not options.get('dont_run_reactor'):
            reactor.run()
