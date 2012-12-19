from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = 'Runs an COMaster emulator'
    def handle_noargs(self, **options):
        print "Running emulator"
