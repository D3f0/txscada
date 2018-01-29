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
Unit tests for asynqueue.base
"""

import time, random, threading
from twisted.internet import defer
from twisted.trial.unittest import TestCase

from util import base
from util import MockWorker


VERBOSE = False


class Test_Priority(TestCase):
    def setUp(self):
        self.heap = base.Priority()

    def test_getInOrder(self):
        dList = []
        for item in (2,1,4,0,3):
            self.heap.put(item)
        for item in xrange(5):
            d = self.heap.get()
            d.addCallback(self.failUnlessEqual, item)
            dList.append(d)
        return defer.DeferredList(dList)

    def test_getBeforePut(self):
        dList, items = [], []
        for item in xrange(5):
            self.heap.put(item)
        for item in xrange(5):
            d = self.heap.get()
            d.addCallback(items.append)
            dList.append(d)
        return defer.DeferredList(dList).addCallback(
            lambda _: self.failUnlessEqual(sum(items), 10))
    
    def test_cancel(self):
        dList, items = [], []
        for item in xrange(5):
            self.heap.put(item)
        self.heap.cancel(lambda x: x is 2)
        for item in xrange(4):
            d = self.heap.get()
            d.addCallback(items.append)
            dList.append(d)
        return defer.DeferredList(dList).addCallback(
            lambda _: self.failUnlessEqual(items, [0,1,3,4]))


class Test_TaskQueue_Generic(TestCase):
    def setUp(self):
        self.queue = base.TaskQueue()

    def tearDown(self):
        return self.queue.shutdown()

    def test_oneTask(self):
        worker = MockWorker(0.5)
        self.queue.attachWorker(worker)
        d = self.queue.call(lambda x: 2*x, 15)
        d.addCallback(self.failUnlessEqual, 30)
        return d

    def test_oneWorker(self):
        N = 30
        mutable = []

        def checkResults(null):
            self.failUnlessEqual(len(mutable), N)
            self.failUnlessEqual(
                sum(mutable),
                sum([2*x for x in xrange(N)]))

        worker = MockWorker(0.01)
        self.queue.attachWorker(worker)
        dList = []
        for x in xrange(N):
            d = self.queue.call(lambda y: 2*y, x)
            d.addCallback(lambda result: mutable.append(result))
            dList.append(d)
        d = defer.DeferredList(dList)
        d.addCallback(checkResults)
        return d

    def test_multipleWorkers(self):
        N = 100
        mutable = []

        def checkResults(null):
            self.failUnlessEqual(len(mutable), N)
            self.failUnlessEqual(
                sum(mutable),
                sum([2*x for x in xrange(N)]))

        for runDelay in (0.05, 0.1, 0.4):
            worker = MockWorker(runDelay)
            ID = self.queue.attachWorker(worker)
            worker.ID = ID
        dList = []
        for x in xrange(N):
            d = self.queue.call(lambda y: 2*y, x)
            d.addCallback(lambda result: mutable.append(result))
            dList.append(d)
        d = defer.DeferredList(dList)
        d.addCallback(checkResults)
        return d

