from django.core.management.base import NoArgsCommand
from django.core.management.commands.runserver import BaseRunserverCommand
from django.core.management import call_command
from django.conf import settings
from utils.autoreload import python_reloader as reloader
from multiprocessing import Process
from twisted.internet import error
from socketserver import sockjs_server, forwarder
from copy import copy
from optparse import make_option
import atexit
import os

def term(*stuff):

    print "Term", ", ".join(map(repr, stuff))
    os._exit(3)

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        reloader(self.inner_run, args=(), kwargs=options)


    def inner_run(self, **options):
        from time import sleep
        import os
        import signal
        signal.signal(signal.SIGTERM, term)

        try:
            while True:
                sleep(.5)
                print os.getpid()
        except SystemExit, e:
            print "*"
            raise e