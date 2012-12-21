# encoding: utf-8

from twisted.internet import protocol, reactor
from logging import getLogger
from construct import Container
from construct.core import FieldError, Struct
from twisted.internet.protocol import ClientFactory
from ..constructs import (MaraFrame, Event)
from protocols.constants import MAX_SEQ, MIN_SEQ
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from datetime import datetime
from ..utils.bitfield import bitfield
from ..constructs import upperhexstr
import models
from copy import copy
import random

logger = getLogger(__name__)

#===============================================================================
# COMaster emulation
#===============================================================================

class MaraServer(protocol.Protocol):
    '''
    Works as COMaster development board
    It replies commands 0x10 based on the definition
    in the comaster instance (a DB table).
    '''
    comaster = None
    def __init__(self):
        """Crea un protocolo que emula a un COMaster"""
        self.input = Container()
        self.output = Container()


    def connectionMade(self,):
        """docstring for connectionMade"""
        #from ipdb import set_trace; set_trace()
        logger.debug("Conection made to %s:%s" % self.transport.client)

    def dataReceived(self, data):
        """Recepción de datos"""
        try:
            self.input = MaraFrame.parse(data)
        except FieldError as e:
            # If the server has no data, it does not matter
            logger.warn("Error de pareso: %s" % upperhexstr(data))
        self.maraPackageReceived()

    def maraPackageReceived(self):
        """Note: Input holds input package parse results"""
        if self.input.command == 0x10:
            # Response for command 0x10
            print "Responding Mara Frame from: %s" % self.transport
            self.transport.write(self.makeResponse10())
        else:
            print "Not responding to package %x" % self.input.command

    def makeResponse10(self):
        self.output = copy(self.input)
        self.output.source, self.output.dest = self.output.dest, self.output.source

        ais = [ random.randrange(0, 254) for _ in xrange(9) ]

        self.output.payload_10 = Container(
            canvarsys=5,
            varsys=[0x1234, 0xfeda],
            candis=4,
            dis=[0x45AA, 0xFF],
            canais=2 * len(ais) + 1, # Two byte vars
            ais=ais,
            canevs=0,
            event=[]
        )

        return MaraFrame.build(self.output)




    def connectionLost(self, reason):
        print "Conexion con %s:%s terminada" % self.transport.client


class MaraServerFactory(protocol.Factory):
    protocol = MaraServer

