# sAsync:
# An enhancement to the SQLAlchemy package that provides persistent
# dictionaries, text indexing and searching, and an access broker for
# conveniently managing database access, table setup, and
# transactions. Everything can be run in an asynchronous fashion using the
# Twisted framework and its deferred processing capabilities.
#
# Copyright (C) 2006 by Edwin A. Suominen, http://www.eepatents.com
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
Unit tests for sasync.parray.py.
"""
import random
from twisted.internet import defer
from twisted.trial.unittest import TestCase

import sqlalchemy as SA

from sasync.database import transact, AccessBroker
import sasync.parray as parray
import mock

GROUP_ID = 123
VERBOSE = False

db = 'parray.db'


class Parray:
    def setUp(self):
        self.a = parray.PersistentArray(GROUP_ID, "sqlite:///%s" % db)
        # This shouldn't be needed in normal usage, but for test code we may
        # access the table before a "real" transaction.
        return self.a.t.startup()

    def tearDown(self):
        def _tearDown():
            sa = self.a.t.sasync_array
            sa.delete(sa.c.group_id == GROUP_ID).execute()

        d = self.a.t.deferToQueue(_tearDown, niceness=19)
        d.addCallback(self.a.shutdown)
        return d

    def loadFromDB(self, x, y, z):
        def _loadFromDB():
            sa = self.a.t.sasync_array
            row = sa.select(
                SA.and_(sa.c.group_id == GROUP_ID,
                        sa.c.x == SA.bindparam('x'),
                        sa.c.y == SA.bindparam('y'),
                        sa.c.z == SA.bindparam('z'))).execute().fetchone()
            return row

        return self.a.t.deferToQueue(_loadFromDB)
    
    def writeToDB(self, x, y, z, value):
        def _writeToDB():
            self.a.t.sasync_array.insert().execute(
                group_id=GROUP_ID,
                x=hash(x), y=hash(y), z=hash(z), value=value)
        
        return self.a.t.deferToQueue(_writeToDB)

    def clearDB(self):
        def _clearDB():
            self.a.t.sasync_array.delete(
                self.a.t.sasync_array.c.group_id == GROUP_ID).execute()
        
        return self.a.t.deferToQueue(_clearDB)


class TestPersistentArray(Parray, TestCase):
    elements = ((1,2,3,'a'), (2,3,4,'b'), (4,5,6,'c'))

    def writeStuff(self, null):
        dList = []
        for element in self.elements:
            dList.append(self.writeToDB(*element))
        return defer.DeferredList(dList)
    
    def testWriteAndGet(self):
        d = self.clearDB()
        d.addCallback(self.writeStuff)
        d.addCallback(lambda _: self.a.get(1,2,3))
        d.addCallback(self.failUnlessEqual, 'a')
        d.addCallback(lambda _: self.a.get(2,3,4))
        d.addCallback(self.failUnlessEqual, 'b')
        d.addCallback(lambda _: self.a.get(4,5,6))
        d.addCallback(self.failUnlessEqual, 'c')
        return d

    def testOverwriteAndGet(self):
        d = self.clearDB()
        d.addCallback(self.writeStuff)
        d.addCallback(lambda _: self.a.get(1,2,3))
        d.addCallback(self.failUnlessEqual, 'a')
        d.addCallback(lambda _: self.a.set(1,2,3, 'foo'))
        d.addCallback(lambda _: self.a.get(1,2,3))
        d.addCallback(self.failUnlessEqual, 'foo')
        return d
    
    def testDeleteAndCheck(self):
        d = self.clearDB()
        d.addCallback(self.writeStuff)
        d.addCallback(lambda _: self.a.delete(1,2,3))
        d.addCallback(lambda _: self.loadFromDB(1,2,3))
        d.addCallback(self.failIf)
        return d

    def testClearAndCheck(self):
        def check(null):
            d1 = defer.Deferred()
            @defer.deferredGenerator
            def _check():
                for element in self.elements:
                    wfd = defer.waitForDeferred(self.loadFromDB(*element[0:3]))
                    yield wfd
                    result = wfd.getResult()
                    self.failIf(
                        result, "Should have empty row, got '%s'" % result)
            d2 = _check()
            d2.chainDeferred(d1)
            return d1
        
        d = self.clearDB()
        d.addCallback(self.writeStuff)
        d.addCallback(lambda _: self.a.clear())
        d.addCallback(check)
        return d

    def testSetAndGet(self):
        d = self.clearDB()
        d.addCallback(lambda _: self.a.set(1,2,3, True))
        d.addCallback(lambda _: self.a.get(1,2,3))
        d.addCallback(self.failUnlessEqual, True)
        return d

    def testDimensions(self):
        d = self.clearDB()
        d.addCallback(self.writeStuff)
        d.addCallback(lambda _: self.a.get(1,2,4))
        d.addCallback(self.failUnlessEqual, None)
        d.addCallback(lambda _: self.a.get(1,3,3))
        d.addCallback(self.failUnlessEqual, None)
        d.addCallback(lambda _: self.a.get(2,2,3))
        d.addCallback(self.failUnlessEqual, None)
        return d
    
