# encoding: utf-8

from __future__ import print_function

from copy import copy
from datetime import datetime
import logging
import random

from ..constructs import upperhexstr, dtime2dict
from .common import MaraFrameBasedProtocol
from construct import Container
from construct.core import FieldError
from protocols.constructs import Event, MaraFrame
from twisted.internet import protocol


def random_bytes(count):
    '''
    Mara aware value generator. Creates the Mara offset and values
    :returns (offset, data)
    '''
    return (count+1, [random.randrange(0, 0xFF) for x in xrange(count)])


def random_words(count):
    '''
    Mara aware value generator. Creates the Mara offset and values
    :returns (offset, data)
    '''
    return ((count*2)+1, [random.randrange(0, 0xFFFF) for x in range(count)])


class MaraServer(MaraFrameBasedProtocol):
    '''
    Works as COMaster development board
    It replies commands 0x10 based on the definition
    in the comaster instance (a DB table).
    '''

    def connectionMade(self,):
        self.logger.debug("Conection made to %s:%s" % self.transport.client)
        self.input = Container()
        self.output = None

    def sendCotainer(self, container):
        '''Convenience method for publishing when data is sent'''
        assert isinstance(container, Container)
        data = self.construct.build(container)
        self.logger.info("Reponding -> %s", upperhexstr(data))
        self.transport.write(data)

    def dataReceived(self, data):
        try:
            self.input = MaraFrame.parse(data)
            self.maraPackageReceived()
        except FieldError:
            # If the server has no data, it does not matter
            self.input = None
            self.logger.warn("Error de pareso: %s" % upperhexstr(data))

    def maraPackageReceived(self):
        """Note: Input holds input package parse results"""
        if self.input.command == 0x10:
            # Response for command 0x10
            self.logger.info("Responding Mara Frame from: %s", self.transport)

            self.sendCotainer(self.buildPollResponse())
        else:
            self.logger.warning("Not responding to package %x", self.input.command)

    def buildPollResponse(self):
        '''It should reassemble what the COMaster does'''

        output = copy(self.input)
        # exchange input
        output.source, output.dest = self.input.dest, self.input.source
        # show current squence number
        self.logger.info("Sequence: %d", self.input.sequence)

        canvarsys, varsys = random_bytes(60)
        candis, dis = random_words(12)
        canais, ais = random_words(22)
        output.payload_10 = Container(
            canvarsys=canvarsys,
            varsys=varsys,
            candis=candis,
            dis=dis,
            canais=canais,
            ais=ais,
            event=[],
            canevs=1,
        )
        return output



class MaraServerFactory(protocol.Factory):
    protocol = MaraServer

    def buildProtocol(self, addr):
        instance = protocol.Factory.buildProtocol(self, addr)
        instance.construct = MaraFrame
        instance.logger = logging.getLogger('commands')
        return instance
