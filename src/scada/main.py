'''
Created on 06/08/2009

@author: defo
'''
from twisted.internet import reactor, protocol

class EchoProtocol(protocol.Protocol):

    def connectionLost(self, reason):
        print "Bye"
        reactor.stop()
        

    def dataReceived(self, data):
        self.transport.write("%d\n" % len(data))
        
    

class EchoFactory(protocol.ClientFactory):
    protocol = EchoProtocol
    
reactor.listenTCP(9000, EchoFactory() )
reactor.run()