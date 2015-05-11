from twisted.internet.defer import DeferredQueue
from twisted.internet import reactor


def on_get(data):
    print data

q = DeferredQueue()
q.get().addCallback(on_get)


def send_data(q, d):
    q.put(d)

reactor.callLater(1, send_data, q, 1)
reactor.callLater(2, send_data, q, 2)
reactor.callLater(3, reactor.stop)

reactor.run()
