# encoding: utf-8

from __future__ import print_function

from copy import copy
import logging
import random
import os

from ..constructs import upperhexstr
from protocols.constants import commands
from construct import Container
from construct.core import FieldError
from protocols.constructs import MaraFrame  # Event
from twisted.internet import protocol
from protocols.constructs.structs import hexstr2buffer
import logging

random.seed(os.getpid())


def random_bytes(count):
    """
    Mara aware value generator. Creates the Mara offset and values
    :returns (offset, data)
    """
    return (count+1, [random.randrange(0, 0xFF) for x in xrange(count)])


def random_words(count):
    """
    Mara aware value generator. Creates the Mara offset and values
    :returns (offset, data)
    """
    return ((count*2)+1, [random.randrange(0, 0xFFFF) for x in range(count)])


class MaraServer(protocol.Protocol):
    """
    Works as COMaster development board
    It replies commands 0x10 based on the definition
    in the comaster instance (a DB table).
    """

    def connectionMade(self,):
        self.logger.debug("Conection made to %s:%s" % self.transport.client)
        self.input = Container()
        self.output = None
        self.last_seq = None
        self.last_peh = None
        self.peh_count = 0

    def sendCotainer(self, container):
        """Convenience method for publishing when data is sent"""
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
            if self.input.sequence == self.last_seq and self.output:
                self.logger.debug("Sending same package!")
            else:
                self.last_seq = self.input.sequence
                self.output = self.buildPollResponse()
            self.sendCotainer(self.output)
        elif self.input.command == commands.PEH.value:

            self.logger.info("PEH: %s", self.input.peh)
        else:
            self.logger.warning("Not responding to package %x", self.input.command)

    def buildPollResponse(self):
        """It should reassemble what the COMaster does"""

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

        if random.choice((True, False)):
            new_seq = random.randrange(50, 150)
            self.logger.info("Mangling seuqnce to: %d", new_seq)
            output.sequence = new_seq
        return output

    def sendFixedRespose(self):

        bad_data = (
            'FE 08 0A 01 06 10 F1 E6 19 16 2D 2A 00 40 01 A4 50 00 00 00 00 00 00 00 00'
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
        )

        self.transport.write(hexstr2buffer(bad_data))


class ServerLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return  '[%s] %s' % ("SERVER", msg), kwargs


class MaraServerFactory(protocol.Factory):
    protocol = MaraServer

    def __init__(self, logger=None):
        if not logger:
            logger = logging.getLogger('')
        self.logger = ServerLogAdapter(logger, {})
        self.logger.info("Server Factory created.")

    def buildProtocol(self, addr):
        self.logger.info("Building protocol for %s", addr)
        proto = protocol.Factory.buildProtocol(self, addr)
        proto.construct = MaraFrame
        proto.logger = self.logger
        return proto
