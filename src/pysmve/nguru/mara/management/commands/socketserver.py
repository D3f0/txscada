from django.core.management.base import NoArgsCommand
from django.conf import settings
from multiprocessing import Process
from twisted.internet import reactor, error, protocol
from txsockjs.factory import SockJSFactory
import zmq
from txzmq import ZmqEndpoint, ZmqFactory, ZmqSubConnection


def forwarder(**options):
    '''Forwarder PUB/SUB'''
    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind(settings.FORWARDER_SUBSCRIBER_ENDPOINT)

        frontend.setsockopt(zmq.SUBSCRIBE, "")

        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind(settings.FORWARDER_PUBLISHER_ENDPOINT)

        zmq.device(zmq.FORWARDER, frontend, backend)
    except (Exception, KeyboardInterrupt) as e:
        print e
        print "bringing down zmq device"
    finally:
        frontend.close()
        backend.close()
        context.term()


def serve(**options):
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
    endpoint = '%s://localhost:%d' % (settings.FORWARDER_SUBSCRIBER_TRANSPORT,
                                      settings.FORWARDER_SUBSCRIBER_PORT)
    e = ZmqEndpoint("connect", endpoint)
    subscription = ZmqSubConnection(zf, e)
    subscription.subscribe("")

    class SockJSProtocol(protocol.Protocol):

        instances = []

        def __init__(self, *largs, **kwargs):
            print "SockJS"
            #protocol.Protocol.__init__(*largs, **kwargs)
            SockJSProtocol.instances.append(self)

        def dataReceived(self, data):
            print data

        def connectionLost(self, reason):
            print "Cerrando Socket"

            self.instances.remove(self)
            protocol.Protocol.connectionLost(self, reason)

        @classmethod
        def broadcast(cls, data, *largs, **kwargs):
            for conn in cls.instances:
                try:
                    conn.transport.write(data)
                except Exception as e:
                    pass


    subscription.gotMessage = SockJSProtocol.broadcast

    factory = protocol.ServerFactory()
    factory.protocol = SockJSProtocol
    reactor.listenTCP(8888, SockJSFactory(factory, options))

    reactor.run()
    print "Closing bridge"



class Command(NoArgsCommand):
    def handle_noargs(self, **options):

        p1 = Process(target=forwarder, kwargs=options)
        p2 = Process(target=serve, kwargs=options)
        p1.start()
        p2.start()
        try:
            p1.join()
            p2.join()
        except KeyboardInterrupt, error.ReactorNotRunning:
            p1.terminate()
            p2.terminate()
