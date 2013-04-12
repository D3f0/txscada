import os
import sys
import socket
from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.core.servers.basehttp import WSGIServerException
from utils.autoreload import python_reloader as reloader
from multiprocessing import Process
from twisted.internet import error
from socketserver import sockjs_server, forwarder
from copy import copy
from optparse import make_option
import functools
from twisted.internet import inotify, reactor, task
from twisted.python import filepath


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--noreload',
                    action='store_false',
                    dest='use_reloader',
                    default=True,
                    help='Tells Django to NOT use the auto-reloader.'),
    )

    processes = []

    def file_changed(self, ignored, filepath, mask):
       """
       For historical reasons, an opaque handle is passed as first
       parameter. This object should never be used.

       @param filepath: FilePath on which the event happened.
       @param mask: inotify event as hexadecimal masks
       """
       print mask
       print "event %s on %s" % (
           ', '.join(inotify.humanReadableMask(mask)), filepath)

    def start_monitoring_file_changes(self, path=None):
        if path is None:
            path = os.getcwd()
        self.notifier = inotify.INotify()
        self.notifier.startReading()
        self.notifier.watch(filepath.FilePath(path), callbacks=[self.file_changed])

    def restart_services_if_changes(self):
        pass

    def handle_noargs(self, **options):
        self.options = options
        self.start_monitoring_file_changes()
        l = task.LoopingCall(self.restart_services_if_changes)
        l.start(1.0)  # call every second
        reactor.callWhenRunning(self.start_services)
        try:
            reactor.run()
        except KeyboardInterrupt:
            self.terminate_processes()

        #reloader(self.inner_run, args=(), kwargs=options)
    def start_services(self):

        runserver_args = copy(self.options)
        runserver_args.update(use_reloader=False)
        p1 = Process(target=call_command, args=('runserver',), kwargs=runserver_args)
        p2 = Process(target=forwarder, kwargs=self.options)
        p3 = Process(target=sockjs_server, kwargs=dict(configure=True))

        # Register processes to terminate when reloader emmits SIGTERM
        Command.processes = [p1, p2, p3]

        p1.start()
        p2.start()
        p3.start()
        print "PROcess started"
        # try:
        #     p1.join()
        #     p2.join()
        #     p3.join()
        # except (KeyboardInterrupt, error.ReactorNotRunning, socket.error,
        #     WSGIServerException) as e:
        #     pass
        # except Exception, e:
        #     print e
        # finally:
        #     self.terminate_processes()

    @classmethod
    def terminate_processes(cls, *args):
        '''Receives *args to be suitable for signal handling'''
        print "*** Closing services ***"
        for proc in cls.processes:
            try:
                proc.terminate()
            except Exception:
                pass