

"""
Example txzmq client.

    examples/pub_sub.py --method=bind --endpoint=ipc:///tmp/sock --mode=publisher

    examples/pub_sub.py --method=connect --endpoint=ipc:///tmp/sock --mode=subscriber
"""
import os
import sys
import time
from optparse import OptionParser

from twisted.internet import reactor, defer

rootdir = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.append(rootdir)
os.chdir(rootdir)

from txzmq import ZmqEndpoint, ZmqFactory, ZmqPubConnection, ZmqSubConnection


parser = OptionParser("")
parser.add_option("-m", "--method", dest="method", 
                  help="0MQ socket connection: bind|connect",
                  default='bind')
parser.add_option("-e", "--endpoint", dest="endpoint", help="0MQ Endpoint")
parser.add_option("-M", "--mode", dest="mode", help="Mode: publisher|subscriber")
parser.set_defaults(method="connect", endpoint="tcp://127.0.0.1:1024")

(options, args) = parser.parse_args()

zf = ZmqFactory()
e = ZmqEndpoint(options.method, options.endpoint)

if options.mode == "publisher":
    print "Publisher", options
    s = ZmqPubConnection(zf, e)

    def publish():
        data = str(time.time())
        print "publishing %r" % data
        s.publish(data)

        reactor.callLater(1, publish)

    publish()
else:
    print "Subscriber", options
    s = ZmqSubConnection(zf, e)
    s.subscribe("")

    def doPrint(*args):
        print "message received: %r" % (args, )

    s.gotMessage = doPrint

reactor.run()