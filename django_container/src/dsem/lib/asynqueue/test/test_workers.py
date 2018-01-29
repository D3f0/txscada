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
Unit tests for asynqueue.workers
"""

import time, random, threading
import zope.interface
from twisted.internet import defer
from twisted.trial.unittest import TestCase

from util import base, workers, errors


VERBOSE = False


class NoCAttr(object):
    zope.interface.implements(workers.IWorker)
    def __init__(self):
        self.iQualified = []

class NoIAttr(object):
    zope.interface.implements(workers.IWorker)
    cQualified = []

class AttrBogus(object):
    zope.interface.implements(workers.IWorker)
    cQualified = 'foo'
    def __init__(self):
        iQualified = 'bar'

class AttrOK(object):
    zope.interface.implements(workers.IWorker)
    cQualified = ['foo']
    def __init__(self):
        self.iQualified = ['bar']


class TestIWorker(TestCase):
    def testInvariantCheckClassAttribute(self):
        worker = AttrOK()
        try:
            workers.IWorker.validateInvariants(worker)
        except:
            self.fail(
                "Acceptable class attribute shouldn't raise an exception")
        for worker in [x() for x in (NoCAttr, NoIAttr, AttrBogus)]:
            self.failUnlessRaises(
                errors.InvariantError,
                workers.IWorker.validateInvariants, worker)
    
    def testInvariantCheckInstanceAttribute(self):
        worker = AttrOK()
        for attr in (None, []):
            if attr is not None:
                worker.iQualified = attr
            try:
                workers.IWorker.validateInvariants(worker)
            except:
                self.fail(
                    "Acceptable instance attribute shouldn't raise exception")
        worker.iQualified = 'foo'
        self.failUnlessRaises(
            errors.InvariantError,
            workers.IWorker.validateInvariants, worker)


class TestThreadWorker(TestCase):
    def setUp(self):
        self.worker = workers.ThreadWorker()
        self.queue = base.TaskQueue()
        self.queue.attachWorker(self.worker)

    def tearDown(self):
        return self.queue.shutdown()

    def _blockingTask(self, x):
        delay = random.uniform(0.1, 1.0)
        if VERBOSE:
            print "Running %f sec. task in thread %s" % \
                  (delay, threading.currentThread().getName())
        time.sleep(delay)
        return 2*x

    def testShutdown(self):
        def checkStopped(null):
            self.failIf(self.worker.thread.isAlive())

        d = self.queue.call(self._blockingTask, 0)
        d.addCallback(lambda _: self.queue.shutdown())
        d.addCallback(checkStopped)
        return d

    def testShutdownWithoutRunning(self):
        def checkStopped(null):
            self.failIf(self.worker.thread.isAlive())

        d = self.queue.shutdown()
        d.addCallback(checkStopped)
        return d

    def testStop(self):
        def checkStopped(null):
            self.failIf(self.worker.thread.isAlive())

        d = self.queue.call(self._blockingTask, 0)
        d.addCallback(lambda _: self.worker.stop())
        d.addCallback(checkStopped)
        return d

    def testOneTask(self):
        d = self.queue.call(self._blockingTask, 15)
        d.addCallback(self.failUnlessEqual, 30)
        return d

    def testMultipleWorkers(self):
        N = 20
        mutable = []

        def gotResult(result):
            if VERBOSE:
                print "Task result: %s" % result
            mutable.append(result)

        def checkResults(null):
            self.failUnlessEqual(len(mutable), N)
            self.failUnlessEqual(
                sum(mutable),
                sum([2*x for x in xrange(N)]))

        # Create and attach two more workers, for a total of three
        for null in xrange(2):
            worker = workers.ThreadWorker()
            self.queue.attachWorker(worker)
        dList = []
        for x in xrange(N):
            d = self.queue.call(self._blockingTask, x)
            d.addCallback(gotResult)
            dList.append(d)
        d = defer.DeferredList(dList)
        d.addCallback(checkResults)
        return d
