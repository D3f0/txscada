# AsynQueue:
# Asynchronous task queueing based on the Twisted framework, with task
# prioritization and a powerful worker/manager interface.
#
# Copyright (C) 2006-2007 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
An IWorker implementation using Perspective Broker (PB) over STDIO.

Based on coding by Konrads Smelkovs
"""

import sys, os.path
from twisted.internet import protocol, stdio, reactor, defer
from twisted.spread import pb

import jobs

CHILD_CODE = """
import os, sys
os.renice(int(sys.argv[-1]))
from asynqueue import processworker
processworker.runAsChild()
"""


class ProtocolWrapper(protocol.ProcessProtocol):
    """
    I wrap a L{Protocol} instance in a L{ProcessProtocol} instance so that...
    """
    def __init__(self, proto, startCallback=None, stopCallback=None):
        self.proto = proto
        self.startCallback = startCallback
        self.stopCallback = stopCallback

    def connectionMade(self):
        """
        Direct mapping of the protocol's C{connectionMade} method.
        """
        self.proto.connectionMade()
        if callable(self.startCallback):
            self.startCallback()
    
    def outReceived(self, data):
        """
        Output received from the process via STDOUT is piped to the protocol as
        data received.
        """
        self.proto.dataReceived(data)

    def processEnded(self, reason):
        """
        When the process ends, the connection is lost.
        """
        self.connectionLost(reason)
    
    def makeConnection(self, transport):
        """
        """
        self.proto.transport = transport
        self.connectionMade()
        
    def dataReceived(self, data):
        """
        Direct mapping of the protocol's C{dataReceived} method.
        """
        self.proto.dataReceived(data)
        
    def connectionLost(self, reason):
        """
        Direct mapping of the protocol's C{connectionLost} method.
        """
        self.proto.connectionLost(reason)
        if callable(self.stopCallback):
            self.stopCallback()


class ChildManager(jobs.JobManager):
    """
    I am a L{jobs.JobManager} that manages a pool of one or more child python
    interpreters as at least some of its workers.
    """
    def _get_children(self):
        if not hasattr(self, '_children'):
            self._children = {}
        return self._children
    children = property(_get_children)
    
    @defer.deferredGenerator
    def startup(self, N=1, niceness=0):
        """
        Starts I{N} child interpreters and attaches instances of
        L{jobs.ChildWorker} for each of them to my queue.

        The workers are set to accept just one job run at a time because
        network latency isn't an issue. The PB connection is via STDIO.

        Returns a deferred that fires with a list of the IDs for the
        interpreters when they have all been started and the queue is ready to
        accept jobs for them.
        """
        for k in xrange(N):
            wfd = defer.waitForDeferred(self.spawnChild(niceness))
            yield wfd
            process, root = wfd.getResult()
            wfd = defer.waitForDeferred(self.attachChild(root, 1))
            yield wfd
            childID = wfd.getResult()
            self.children[childID] = process
        yield self.children.keys()
    
    def spawnChild(self, niceness=0):
        """
        Connects my factory through STDIO to a child python interpreter process.

        The child process should be enabled through a STDIO-wrapped version of
        its server-side PB broker.

        Returns a deferred that fires with the child's process and PB root
        objects.
        """
        if not isinstance(niceness, int) or niceness < 0 or niceness > 19:
            raise TypeError("Niceness level must be an integer 0-19")
        factory = pb.PBClientFactory()
        broker = factory.buildProtocol(('127.0.0.1',))
        d = defer.Deferred()
        wrappedProtocol = ProtocolWrapper(
            broker, startCallback=lambda: d.callback(None))
        code = "; ".join(CHILD_CODE.strip().split("\n"))
        args = (sys.executable, '-c', code, str(niceness))
        process = reactor.spawnProcess(
            wrappedProtocol, sys.executable, args=args, env=None)
        d.addCallback(lambda _: factory.getRootObject())
        d.addCallback(lambda root: (process, root))
        return d
    
    def shutdown(self):
        def wrapUp(null):
            for process in self.children.itervalues():
                process.loseConnection()
            self.children.clear()
        
        return jobs.JobManager.shutdown(self).addCallback(wrapUp)

    def detachChild(self, childID):
        result = jobs.JobManager.detachChild(self, childID)
        if childID in self.children:
            process = self.children.pop(childID)
            process.loseConnection()
        return result


def runAsChild():
    """
    This function takes care of everything needed for a Python interpreter to
    act as a child process worker.
    """
    root = jobs.ChildRoot()
    root.trusted = True
    factory = pb.PBServerFactory(root)
    broker = factory.buildProtocol(('127.0.0.1',))
    wrappedProtocol = ProtocolWrapper(broker)
    stdio.StandardIO(wrappedProtocol)
    reactor.run()
