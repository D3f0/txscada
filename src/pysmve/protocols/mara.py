from twisted.internet import portocol
from logging import getLogger


# Definiciones para mara 14 v7

logger = getLogger(__name__)

class MaraClientProtocol(protocol.Protocol):
    def connectionMade(self):
        logger.debug("Conection made %s" % self.endpoint)
    
class MaraClientProtocolFactory(protocol.Factory):
    pass


class MaraServer(protocol.Protocol):
    '''Emula el COMaster'''
    def __init__(self, root):
        """Crea un protocolo que emula a un COMaster"""
        self.root = root # Referencia al comaster
        
    
    def connectionMade(self, arg):
        """docstring for connectionMade"""
        logger.debug("Servidor conectado")
        
    def dataReceived(self, data):
        """Recepción de datos"""
        pass
    



        
    
    
class MaraServerFactory(protocol.Protocol):
    protocol = MaraServer
    
    def buildProtocol(self, addr):
        logger.debug("Creando protocolo para %s" % addr)
        instance = self.protocol(self)
        return instance
    
    


        