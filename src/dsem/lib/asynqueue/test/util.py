# Twisted Goodies:
# Miscellaneous add-ons and improvements to the separately maintained and
# licensed Twisted (TM) asynchronous framework. Permission to use the name was
# graciously granted by Twisted Matrix Laboratories, http://twistedmatrix.com.
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
Mock objects for twisted_goodies.taskqueue unit tests
"""

import sys, os.path
from zope.interface import implements
from twisted.internet import reactor, defer

# Intelligent import of the modules under test
testPath = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, testPath)
# The modules under test
import base, tasks, workers, errors


VERBOSE = False


class MockTask(object):
    def __init__(self, f, args, kw, priority, series, timeout=None):
        self.ran = False
        self.callTuple = (f, args, kw)
        self.priority = priority
        self.series = series
        self.d = defer.Deferred()
    
    def __cmp__(self, other):
        if other is None:
            return -1
        return cmp(self.priority, other.priority)

    def __str__(self):
        return str(self.callTuple[0])

    def startTimer(self):
        pass


class MockWorker(object):
    implements(workers.IWorker)

    cQualified = []

    def __init__(self, runDelay=0.0):
        self.runDelay = runDelay
        self.ran = []
        self.isShutdown = False
        self.iQualified = []

    def setResignator(self, callableObject):
        pass

    def run(self, task):
        def ran(result, d):
            d.callback(None)
            return result
        
        self.task = task
        self.delayedCall = reactor.callLater(self.runDelay, self._reallyRun)
        d = defer.Deferred()
        task.d.addCallback(ran, d)
        return d
    
    def _reallyRun(self):
        f, args, kw = self.task.callTuple
        result = f(*args, **kw)
        self.ran.append(self.task)
        if VERBOSE:
            ID = getattr(self, 'ID', 0)
            print "Worker %d ran %s = %s" % (ID, str(self.task), result)
        self.task.d.callback(result)

    def stop(self):
        self.isShutdown = True
        if VERBOSE:
            print "Shutting down worker %s" % self
        d = getattr(getattr(self, 'task', None), 'd', None)
        if d is None or d.called:
            d_shutdown = defer.succeed(None)
        else:
            d_shutdown = defer.Deferred()
            d.chainDeferred(d_shutdown)
        return d_shutdown

    def crash(self):
        delayedCall = getattr(self, 'delayedCall', None)
        if delayedCall and delayedCall.active():
            delayedCall.cancel()
            return [self.task]


__all__ = ['base', 'tasks', 'workers', 'errors', 'MockWorker', 'MockTask']
