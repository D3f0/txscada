# encoding: utf-8

from django.core.management.base import NoArgsCommand
from django.conf import settings
from multiprocessing import Process
from twisted.internet import reactor, error, protocol
from txsockjs.factory import SockJSFactory
import zmq
from txzmq import ZmqEndpoint, ZmqFactory, ZmqSubConnection
import json
from copy import copy
from datetime import datetime


def forwarder(**options):
    '''Forwarder PUB/SUB'''
    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind(settings.FORWARDER_SUB_ENDPOINT)

        frontend.setsockopt(zmq.SUBSCRIBE, "")

        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind(settings.FORWARDER_PUB_ENDPOINT)
        print "%s -> %s" % (settings.FORWARDER_PUB_ENDPOINT, settings.FORWARDER_SUB_ENDPOINT)
        zmq.device(zmq.FORWARDER, frontend, backend)
    except (Exception, KeyboardInterrupt) as e:
        print e
        print "bringing down zmq device"
    finally:
        print "Closing forwarder"
        frontend.close()
        backend.close()
        context.term()


def sockjs_server(**options):
    options = {
        'websocket': True,
        'cookie_needed': False,
        'heartbeat': 25,
        'timeout': 5,
        'streaming_limit': 128 * 1024,
        'encoding': 'cp1252',  # Latin1
        'sockjs_url': 'https://d1fxtkz8shb9d2.cloudfront.net/sockjs-0.3.js'
    }

    zf = ZmqFactory()
    endpoint = '%s://localhost:%d' % (settings.FORWARDER_PUB_TRANSPORT,
                                      settings.FORWARDER_PUB_PORT)
    e = ZmqEndpoint("connect", endpoint)
    subscription = ZmqSubConnection(zf, e)
    # Subscripción a todos los mensajes
    subscription.subscribe("")

    class SockJSProtocol(protocol.Protocol):

        DIRECT_FORWARD_MESSAGE_TYPES = ('echo', )

        instances = []

        def __init__(self, *largs, **kwargs):
            print "SockJS"
            #protocol.Protocol.__init__(*largs, **kwargs)
            SockJSProtocol.instances.append(self)

        def dataReceived(self, data_string):
            try:
                data = json.loads(data_string)
                msgtype = data.get('type', None)
                if msgtype in self.DIRECT_FORWARD_MESSAGE_TYPES:
                    self.send_json(data, timestamp=repr(datetime.now()))
            except ValueError as e:
                print e
                self.send_json({'data': data_string, 'type': 'unknown'})

        def send_json(self, data=None, **opts):
            '''Envia una respuesta en JSON por el websocket'''
            if data:
                if isinstance(data, dict):
                    data_safe = copy(data)
                    data_safe.update(opts)
                elif isinstance(data, basestring):
                    try:
                        data_safe = json.loads(data)
                    except ValueError:
                        raise ValueError("Can't convert %s to json" % data)
            else:
                data_safe = opts
            self.transport.write(json.dumps(data_safe))

        def connectionLost(self, reason):
            print "Cerrando Socket"

            self.instances.remove(self)
            protocol.Protocol.connectionLost(self, reason)

        @classmethod
        def broadcast(cls, data, *largs, **kwargs):
            print "Received from forwarder %s" % data
            for conn in cls.instances:
                try:
                    conn.send_json(data)
                except Exception as e:
                    print e

    subscription.gotMessage = SockJSProtocol.broadcast

    factory = protocol.ServerFactory()
    factory.protocol = SockJSProtocol
    reactor.listenTCP(8888, SockJSFactory(factory, options))
    try:
        reactor.run()
    except error.ReactorNotRunning:
        print "Closing bridge"


class Command(NoArgsCommand):
    def handle_noargs(self, **options):

        p1 = Process(target=forwarder, kwargs=options)
        p2 = Process(target=sockjs_server, kwargs=options)
        p1.start()
        p2.start()
        try:
            p1.join()
            p2.join()
        except KeyboardInterrupt, error.ReactorNotRunning:
            p1.terminate()
            p2.terminate()
