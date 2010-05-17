# coding: utf-8
    
from twisted.web2 import server
from twisted.web2.channel import http
from twisted.application import service, internet
from txjsonrpc.web2 import jsonrpc

class Example(jsonrpc.JSONRPC):
    """An example object to be published."""
    addSlash = True
    def jsonrpc_echo(self, request, x):
        """Return all passed args."""
        return x
    def jsonrpc_add(self, request, a, b):
        """Return sum of arguments."""
        return a + b
    
PORT = 8000
print "Iniciando server %s" % PORT
site = server.Site(Example())
channel = http.HTTPFactory(site)
application = service.Application("Example JSON-RPC Server")
jsonrpcServer = internet.TCPServer(PORT, channel)
jsonrpcServer.setServiceParent(application)

if __name__ == "__main__":
    #from twisted.internet import reactor
    
    #reactor.run()
    from twisted.web2 import channel, server
    #toplevel = Toplevel()
    channel.startCGI( site )
 