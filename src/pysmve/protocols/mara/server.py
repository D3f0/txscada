# encoding: utf-8

from twisted.internet import protocol
from logging import getLogger
from construct import Container
from construct.core import FieldError
from ..constructs import (MaraFrame, )
# from protocols.constants import MAX_SEQ, MIN_SEQ
# from twisted.internet.task import LoopingCall
# from twisted.internet.threads import deferToThread
# from ..utils.bitfield import bitfield
from protocols.constructs import Event
from datetime import datetime
from ..constructs import upperhexstr, dtime2dict
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
        # from ipdb import set_trace; set_trace()
        logger.debug("Conection made to %s:%s" % self.transport.client)

    def dataReceived(self, data):
        """Recepción de datos"""
        try:
            self.input = MaraFrame.parse(data)
        except FieldError:
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
        cant_ieds = 5

        svs = self.createSystemVariables(cant_ieds)

        ais = [random.randrange(0, 254) for _ in xrange(9)]
        dis = self.createDIs(ieds=1, ports=3, port_width=16)

        events = self.createDigitalEvents(1)

        self.output.payload_10 = Container(
            # VarSys
            canvarsys=self.length(svs),
            varsys=svs,

            candis=self.length(dis),
            dis=dis,

            canais=self.length(ais),
            ais=ais,

            canevs=len(events) * 10 + 1,
            event=events,
        )
        from pprint import pprint
        pprint(self.output)
        return MaraFrame.build(self.output)

    @staticmethod
    def length(elements):
        '''Length for variables (DI, SV, AI)'''
        return len(elements) * 2 + 1

    def createSystemVariables(self, cant_ieds):
        '''Emula Variables de sistema'''
        base = [0xaabb, 0xccdd, 0xeeff]
        output = []
        for i in range(cant_ieds):
            output.extend(base)
        return output

    def createDIs(self, ieds=1, ports=3, port_width=16, ):
        '''Emula digital inputs'''
        output = []
        for ied in range(ieds):
            for port in range(ports):
                output.extend([random.randrange(0, 2 ** port_width)])
        return output

    def connectionLost(self, reason):
        print "Conexion con %s:%s terminada" % self.transport.client

    def createDigitalEvents(self, qty=1, ports=3, port_width=16):
        output = []
        for i in range(qty):
            ev = Container(evtype="DIGITAL", q=0,
                               addr485=1, # Siempre es el 1
                               bit=random.randrange(1,16),
                               port=random.randrange(1,3),
                               status=random.randrange(0, 1),
                               # Timestamp bytes
                               timestamp=datetime.now()
                               )

            try:
                Event.build(ev)
            except Exception, e:
                print "Error construyendo evento", e
            else:
                print "OK"
                output.append(ev)
        return output

    def createAnalogEvent(self, qty=1):
        pass


class MaraServerFactory(protocol.Factory):
    protocol = MaraServer
