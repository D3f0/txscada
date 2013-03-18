from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.conf import settings
from multiprocessing import Process
from twisted.internet import error
from socketserver import sockjs_server, forwarder
from copy import copy


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        runserver_args = copy(options)
        runserver_args.update(use_reloader=False)
        p1 = Process(target=call_command, args=('runserver',), kwargs=runserver_args)
        p2 = Process(target=forwarder, kwargs=options)
        p3 = Process(target=sockjs_server, kwargs=options)
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
