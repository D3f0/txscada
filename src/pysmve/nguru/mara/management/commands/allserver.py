from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.conf import settings
from multiprocessing import Process
from twisted.internet import error
from socketserver import serve, forwarder


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        p1 = Process(target=call_command, args=('runserver',), kwargs=options)
        p2 = Process(target=forwarder, kwargs=options)
        p3 = Process(target=serve, kwargs=options)
        p1.start()
        p2.start()
        p3.start()
        try:
            p1.join()
            p2.join()
            p3.join()
        except KeyboardInterrupt, error.ReactorNotRunning:
            p1.terminate()
            p2.terminate()
            p3.terminate()
