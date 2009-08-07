'''
Created on 06/08/2009

@author: defo

Implementacion del protcolo PICNET para RESTSCADA.
'''

from twisted.internet import reactor, protocol
from bitstring import BitString


class PicnetProtocol(protocol.Protocol):
    def packageReceived(self, pkg):
        pass
    def dataDiscarded(self, data):
        pass
