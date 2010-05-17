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
Unit tests for asynqueue.jobs
"""

from twisted.internet import defer, reactor
from twisted.python import failure
from twisted.spread import pb, flavors, jelly

import mock, jobs

#import twisted.internet.base
#twisted.internet.base.DelayedCall.debug = True

JOB_ID = 1

JOB_CODE = """
G = []
TRIES = []

def setup(x):
    G.append(x)
    return G

def total():
    return sum(G)

def test(a, b, c=0):
    return a + 2*b + 3*c

def bogusable(x):
    return 1.0 / x

def failFirstTime():
    TRIES.append(None)
    if len(TRIES) == 1:
        raise Exception
    return len(TRIES)

"""


class Thingy(jelly.Jellyable, jelly.Unjellyable):
    def setFoo(self, foo):
        self.foo = foo
    def getFoo(self):
        return self.foo


class Test_ChildRoot_registerClasses(mock.TestCase):
    class TestableChildRoot(jobs.ChildRoot):
        def remote_take(self, thing):
            self.thing = thing
            return True
    
    def setUp(self):
        self.root = self.TestableChildRoot()
        self.root.trusted = True
        self.server = reactor.listenTCP(0, pb.PBServerFactory(self.root))
        clientFactory = pb.PBClientFactory()
        reactor.connectTCP(
            "127.0.0.1", self.server.getHost().port, clientFactory)
        d = clientFactory.getRootObject()
        d.addCallback(lambda x: setattr(self, 'ref', x))
        return d

    def tearDown(self):
        self.ref.broker.transport.loseConnection()
        return self.server.stopListening()
    
    def test_registerClasses(self):
        def check(result):
            self.failUnless(result)
            self.failUnless(isinstance(self.root.thing, Thingy))

        thingy = Thingy()
        stringReps = ["%s.Thingy" % thingy.__module__]
        d = self.ref.callRemote("registerClasses", *stringReps)
        d.addCallback(lambda _: self.ref.callRemote('take', thingy))
        d.addCallback(check)
        return d


class Test_ChildRoot_Other(mock.TestCase):
    def setUp(self):
        self.root = jobs.ChildRoot()
        self.root.trusted = True

    def test_newJob_OK(self):
        result = self.root.remote_newJob(JOB_ID, JOB_CODE)
        self.failUnlessEqual(result[0], True)
        self.failUnlessElementsEqual(
            result[1],
            ['setup', 'total', 'test', 'bogusable', 'failFirstTime'])
    
    def test_newJob_bogus(self):
        bogusJobCode = JOB_CODE + "\nbogus\n"
        result = self.root.remote_newJob(JOB_ID, bogusJobCode)
        self.failUnlessEqual(result[0], False)
        self.failUnless('bogus' in result[1])

    def test_runJob_OK(self):
        def check(result):
            self.failUnlessEqual(result[0], True)
            self.failUnlessEqual(result[1], 600)

        self.root.remote_newJob(JOB_ID, JOB_CODE)
        d = self.root.remote_runJob(JOB_ID, 'test', 100, 100, 100)
        d.addCallback(check)
        return d

    def test_runJob_bogus(self):
        def check(result):
            self.failUnlessEqual(result[0], False)
            self.failUnless('ZeroDivisionError' in result[1])

        self.root.remote_newJob(JOB_ID, JOB_CODE)
        d = self.root.remote_runJob(JOB_ID, 'bogusable', 0)
        d.addCallback(check)
        return d


class Mock_Root(mock.Mock):
    def __init__(self, bogus=False):
        self.bogus = bogus
        self.jobs = {}
        self.callbacks = []
        self.registeredClasses = []

    def notifyOnDisconnect(self, callback):
        self.callbacks.append(callback)

    def callRemote(self, called, *args, **kw):
        if not self.bogus and called == 'newJob':
            jobID, jobCode = args[:2]
            namespace = {}
            exec jobCode in namespace
            self.jobs[jobID] = namespace
            result = (
                True, [x[0] for x in namespace.iteritems() if callable(x[1])])
        elif not self.bogus and called == 'runJob':
            namespace = self.jobs[args[0]]
            calledObject = namespace[args[1]]
            try:
                result = (True, calledObject(*args[2:], **kw))
            except:
                result = (False, failure.Failure().getTraceback())
        elif called == 'registerClasses':
            self.registeredClasses.extend(list(args))
            result = None
        elif called == 'exit':
            result = None
        else:
            result = pb.CopiedFailure(flavors.NoSuchMethod())
        return self.deferToLater(result)


class Mock_Task(mock.Mock):
    def __init__(self, f, args, kw, priority, series):
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

    def called(self):
        return self.d.called

    def callback(self, result):
        self.d.callback(result)
        
    def errback(self, result):
        self.d.errback(result)


class Test_ChildWorker(mock.TestCase):
    def setUp(self):
        self.root = Mock_Root()
        self.root.clearCalls()
        self.worker = jobs.ChildWorker(self.root, noTypeCheck=True)
        return self.root.callRemote('newJob', JOB_ID, JOB_CODE)
    
    def tearDown(self):
        return self.worker.stop()

    def test_SingleTask_OK(self):
        def checkResult(result):
            self.failUnlessEqual(result, (True, 1+2*2+3*3))
            self.nextCall(self.root.calls)
            self.nextCall('Root.callRemote')
            self.nextCall(
                'Root.callRemote',
                ('runJob', JOB_ID, 'test', 1, 2), {'c':3})

        task = Mock_Task('test', (1,2), {'c':3}, 0, JOB_ID)
        self.worker.run(task)
        task.d.addCallback(checkResult)
        return task.d

    def test_SingleTask_Fail(self):
        def checkResult(result):
            self.failUnlessEqual(result[0], False)
            self.failUnless('ZeroDivisionError' in result[1])

        task = Mock_Task('bogusable', (0,), {}, 0, JOB_ID)
        self.worker.run(task)
        task.d.addCallback(checkResult)
        return task.d


class Test_JobManager_Basics(mock.TestCase):
    def setUp(self):
        jobs.ChildWorker._noTypeCheck = True
        self.mgr = jobs.JobManager()
    
    def tearDown(self):
        jobs.ChildWorker._noTypeCheck = False
        return self.mgr.shutdown()

    def _newJob(self):
        self.mgr.jobs[JOB_ID] = (JOB_CODE, 0)
        self.mgr.callsPending[JOB_ID] = {}

    def _attach(self, bogus=False):
        def attached(childID):
            self.childID = childID
            return childID
        
        self.root = Mock_Root(bogus)
        return self.mgr.attachChild(self.root).addCallback(attached)

    def test_attachChild_valid(self):
        def check(null):
            self.nextCall(self.root.calls)
            self.nextCall('Root.callRemote', ('newJob', JOB_ID, JOB_CODE))

        self._newJob()
        return self._attach().addCallback(check)

    def test_attachChild_bogus(self):
        self._newJob()
        return self._attach(bogus=True).addCallback(self.failUnlessEqual, None)

    def test_registerClasses(self):
        def check(null):
            self.failUnlessElementsEqual(
                self.root.registeredClasses, stringReps)

        stringReps = ['foo.bar.SomeClass', 'foo.bar.AnotherClass']
        d = self._attach()
        d.addCallback(lambda _: self.mgr.new(JOB_CODE))
        d.addCallback(lambda _: self.mgr.registerClasses(*stringReps))
        d.addCallback(check)
        return d


class JobManagerBC(mock.TestCase):
    class TestableChildRoot(jobs.ChildRoot):
        trusted = True
    
    def setUp(self):
        self.servers = []
        self.mgr = jobs.JobManager()
        return self.getReferenceToRoot()
    
    def getReferenceToRoot(self):
        def got(ref):
            self.ref = ref
            return ref
        
        root = self.TestableChildRoot()
        server = reactor.listenTCP(0, pb.PBServerFactory(root))
        self.servers.append(server)
        clientFactory = pb.PBClientFactory()
        reactor.connectTCP(
            "127.0.0.1", server.getHost().port, clientFactory)
        return clientFactory.getRootObject().addCallback(got)
    
    def tearDown(self):
        def closeConnection(null):
            self.ref.broker.transport.loseConnection()
            for server in self.servers:
                server.stopListening()
        
        return self.mgr.shutdown().addCallback(closeConnection)
    
    def _newJob(self):
        self.mgr.jobs[JOB_ID] = (JOB_CODE, 0)
        self.mgr.callsPending[JOB_ID] = {}

    def _attach(self, ref):
        def attached(childID):
            self.childID = childID
            return childID
        
        return self.mgr.attachChild(ref, N=1).addCallback(attached)


class Test_JobManager_Admin(JobManagerBC):
    def test_attachChild_withUpdate(self):
        self._newJob()
        # This must run first, on attachment
        d1 = self.mgr.update(JOB_ID, 'setup', 1)
        # The actual attachment event chain
        d2 = self._attach(self.ref)
        d2.addCallback(self.mgr.run, 'setup', 2)
        d2.addCallback(self.failUnlessEqual, [1, 2])
        # Wait for both
        return defer.DeferredList([d1, d2])

    def test_new(self):
        def attached(null):
            self.failUnlessEqual(getattr(self, 'childID', None), 1)
            return self.mgr.new(JOB_CODE).addCallback(check)
        
        def check(jobID):
            self.failUnlessEqual(jobID, 1)
            worker = self.mgr.queue.workers(self.childID)
            self.failUnlessEqual(worker.iQualified, [1])
        
        return self._attach(self.ref).addCallback(attached)

    def test_run_updates(self):
        def gotJobID(jobID):
            d = self.mgr.update(jobID, 'setup', 1)
            d.addCallback(lambda _: self.mgr.update(jobID, 'setup', 2))
            d.addCallback(lambda _: self.mgr.run(jobID, 'total'))
            d.addCallback(self.failUnlessEqual, 3)
            return d
        
        d = self._attach(self.ref)
        d.addCallback(lambda _: self.mgr.new(JOB_CODE))
        d.addCallback(gotJobID)
        return d

    def test_disconnect_cancel(self):
        def gotJobID(jobID):
            self.ref.broker.transport.loseConnection()
            d = self.mgr.run(jobID, 'test', 0, 0).addCallback(runOver)
            self.mgr.cancel(jobID)
            return d

        def runOver(result):
            print "Job Canceled"

        self.fail("Cancel doesn't work after disconnect, fix someday")
        d = self._attach(self.ref)
        d.addCallback(lambda _: self.mgr.new(JOB_CODE))
        d.addCallback(gotJobID)
        return d
        
    def test_disconnect_reassign(self):
        def gotJobID(jobID):
            self.ref.broker.transport.loseConnection()
            return mock.deferToLater(delay=1.0).addCallback(delayDone, jobID)

        def delayDone(null, jobID):
            d = self.mgr.run(jobID, 'test', 1, 2)
            d.addCallback(self.failUnlessEqual, 5)
            self.getReferenceToRoot().addCallback(self._attach)
            return d
        
        d = self._attach(self.ref)
        d.addCallback(lambda _: self.mgr.new(JOB_CODE))
        d.addCallback(gotJobID)
        return d



class Test_JobManager_Run(JobManagerBC):
    def test_run_one(self):
        d = self._attach(self.ref)
        d.addCallback(lambda _: self.mgr.new(JOB_CODE))
        d.addCallback(self.mgr.run, 'test', 10, 20)
        d.addCallback(self.failUnlessEqual, 50)
        return d

    @defer.deferredGenerator
    def test_run_several_sequentially(self):
        results = []
        yield defer.waitForDeferred(self._attach(self.ref))
        wfd = defer.waitForDeferred(self.mgr.new(JOB_CODE))
        yield wfd
        jobID = wfd.getResult()
        for x in xrange(10):
            wfd = defer.waitForDeferred(self.mgr.run(jobID, 'test', x, 0))
            yield wfd
            results.append(wfd.getResult())
        self.failUnlessEqual(results, range(10))

    @defer.deferredGenerator
    def test_run_several_queued(self):
        results = []
        yield defer.waitForDeferred(self._attach(self.ref))
        wfd = defer.waitForDeferred(self.mgr.new(JOB_CODE))
        yield wfd
        jobID = wfd.getResult()
        dList = []
        for x in xrange(10):
            d = self.mgr.run(jobID, 'test', x, 0)
            d.addCallback(results.append)
            dList.append(d)
        yield defer.waitForDeferred(defer.DeferredList(dList))
        self.failUnlessEqual(results, range(10))

    def test_retry_after_failure(self):
        d = self._attach(self.ref)
        d.addCallback(lambda _: self.mgr.new(JOB_CODE))
        d.addCallback(self.mgr.run, 'failFirstTime')
        d.addCallback(self.failUnlessEqual, 2)
        return d
        
