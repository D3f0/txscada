'''
Created on 06/08/2009

@author: defo

Implementacion del protcolo PICNET para RESTSCADA.
'''

from twisted.internet import reactor, protocol
from bitstring import BitString


class PicnetProtocolBase(protocol.Protocol):
    '''
    
    '''
    def packageReceived(self, pkg):
        pass
    def dataDiscarded(self, data):
        pass

class PicnetProtocol(protocol.Protocol):
    # Responde al número de XLS producido por ricardo
    VERSION = (0,11)
    
    
class PicnetPackage(object):
    '''
    Picnet protocol package 
    '''
    def __init__(self):
        pass