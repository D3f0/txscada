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
Unit tests for asynqueue.processworker
"""

from twisted.internet import defer
import mock, processworker


JOB_ID = 1

JOB_CODE = """
def test(a, b, c=0):
    return a + 2*b + 3*c
"""


class Test_Parent(mock.TestCase):
    def setUp(self):
        self.mgr = processworker.ChildManager()

    def tearDown(self):
        return self.mgr.shutdown()

    def test_spawnChild(self):
        def check(result):
            process, root = result
            self.mgr._children = {1:process}
            d = root.callRemote('newJob', JOB_ID, JOB_CODE)
            d.addCallback(self.failUnlessEqual, (True, ['test']))
            return d
        
        return self.mgr.spawnChild().addCallback(check)

    @defer.deferredGenerator
    def test_callOnChild(self):
        wfd = defer.waitForDeferred(self.mgr.spawnChild())
        yield wfd
        process, root = wfd.getResult()
        self.mgr._children = {1:process}
        wfd = defer.waitForDeferred(
            root.callRemote('newJob', JOB_ID, JOB_CODE))
        yield wfd
        self.failUnless(wfd.getResult(), "Child didn't accept job")
        wfd = defer.waitForDeferred(
            root.callRemote('runJob', 1, 'test', 10, 20))
        yield wfd
        status, result = wfd.getResult()
        self.failUnless(status, "Call failed")
        self.failUnlessEqual(result, 50)
        
    @defer.deferredGenerator
    def test_runMultipleChildren(self):
        N = 3
        N_iter = 100
        wfd = defer.waitForDeferred(self.mgr.startup(N))
        yield wfd
        childIDs = wfd.getResult()
        self.failUnlessEqual(len(childIDs), N)
        wfd = defer.waitForDeferred(self.mgr.new(JOB_CODE))
        yield wfd
        jobID = wfd.getResult()
        dList = []
        for k in xrange(N_iter):
            expectedResult = 10*k + 2*20*k + 3*30*k
            d = self.mgr.run(jobID, 'test', 10*k, 20*k, 30*k)
            d.addCallback(self.failUnlessEqual, expectedResult)
            dList.append(d)
        wfd = defer.waitForDeferred(defer.DeferredList(dList))
        yield wfd
        wfd.getResult()
        

                                    
        
