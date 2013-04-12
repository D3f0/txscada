from django.core.management.base import BaseCommand, CommandError
from django.core.handlers.wsgi import WSGIHandler
#from django.utils import autoreload
from trunserv import autoreload

from twisted.application import internet, service, app
from twisted.web import server, resource, wsgi, static
from twisted.python import threadpool, log
from twisted.internet import reactor

from optparse import make_option
import sys
import os
import re


naiveip_re = re.compile(r"""^(?:
(?P<addr>
    (?P<ipv4>\d{1,3}(?:\.\d{1,3}){3}) |         # IPv4 address
    (?P<ipv6>\[[a-fA-F0-9:]+\]) |               # IPv6 address
    (?P<fqdn>[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*) # FQDN
):)?(?P<port>\d+)$""", re.X)
DEFAULT_PORT = "8000"


class Root(resource.Resource):
    def __init__(self, wsgi_resource):
        resource.Resource.__init__(self)
        self.wsgi_resource = wsgi_resource

    def getChild(self, path, request):
        path0 = request.prepath.pop(0)
        request.postpath.insert(0, path0)
        return self.wsgi_resource


def wsgi_resource():
    pool = threadpool.ThreadPool()
    pool.start()
    # Allow Ctrl-C to get you out cleanly:
    reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
    wsgi_resource = wsgi.WSGIResource(reactor, pool, WSGIHandler())
    return wsgi_resource


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noreload', action='store_false', dest='use_reloader',
            default=True, help='Do NOT use the auto-reloader.'),
    )
    help = "Starts a Twisted Web server for development."
    args = '[optional port number, or ipaddr:port]'

    # Validation is called explicitly each time the server is reloaded.
    requires_model_validation = False

    def handle(self, addrport='', *args, **options):
        if not addrport:
            self.addr = ''
            self.port = DEFAULT_PORT
        else:
            m = re.match(naiveip_re, addrport)
            if m is None:
                raise CommandError('"%s" is not a valid port number '
                                   'or address:port pair.' % addrport)
            self.addr, _ipv4, _ipv6, _fqdn, self.port = m.groups()
            if not self.port.isdigit():
                raise CommandError("%r is not a valid port." % self.port)

        if not self.addr:
            self.addr = '127.0.0.1'

        self.run(*args, **options)

    def run(self, *args, **options):
        use_reloader = options.get('use_reloader', True)

        def _inner_run():
            # Initialize logging
            log.startLogging(sys.stdout)

            # Setup Twisted application
            application = service.Application('django')
            wsgi_root = wsgi_resource()
            root = Root(wsgi_root)

            main_site = server.Site(root)
            internet.TCPServer(int(self.port), main_site
                    ).setServiceParent(application)

            service.IService(application).startService()
            app.startApplication(application, False)

            reactor.addSystemEventTrigger('before', 'shutdown',
                    service.IService(application).stopService)

            reactor.run()

        if use_reloader:
            try:
                autoreload.main(_inner_run)
            except TypeError:
                # autoreload was in the middle of something
                pass
        else:
            _inner_run()
