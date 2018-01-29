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
Unit tests for sasync.pdict.py.
"""

import os
from twisted.internet import defer, reactor
from twisted.trial.unittest import TestCase

import sqlalchemy as SA
import sasync
from sasync.pdict import PersistentDict
from sasync.parray import PersistentArray

ID = 341
VERBOSE = False


db = '/tmp/pdict.db'
URL = "sqlite:///%s" % db
sasync.engine(URL)


def itemsEqual(itemsA, itemsB):
    if VERBOSE:
        print "\n%s\n\tvs\n%s\n" % (str(itemsA), str(itemsB))
    for item in itemsA:
        if not itemsB.count(item):
            print "Item '%s' of list A not in list B" % (item,)
            return False
    for item in itemsB:
        if not itemsA.count(item):
            print "Item '%s' of list B not in list A" % (item,)
            return False
    return True


class TestPlayNice(TestCase):
    def testShutdown(self):
        def first(null):
            y = PersistentDict('alpha')
            d = y['eagle']
            d.addCallback(self.failUnlessEqual, 'bald')
            return d
        
        x = PersistentDict('alpha')
        x['eagle'] = 'bald'
        d = x.shutdown()
        d.addCallback(first)
        return d
    
    def testSequentiallyStartedDicts(self):
        x = PersistentDict('alpha')
        y = PersistentDict('bravo')
        
        def first():
            d = x.preload()
            d.addCallback(lambda _: y.preload())
            return d

        def second(null):
            x['a'] = 1
            y['a'] = 10
            return defer.DeferredList([x.deferToWrites(), y.deferToWrites()])

        def third(null):
            self.failUnlessEqual(x['a'], 1)
            self.failUnlessEqual(y['a'], 10)
            return defer.DeferredList([x.shutdown(), y.shutdown()])
        
        d = first()
        d.addCallback(second)
        d.addCallback(third) 
        return d

    def testThreeSeparateDicts(self):
        def first():
            self.x['a'] = 1
            self.y['a'] = 10
            self.z['a'] = 100
            return defer.DeferredList([
                self.x.deferToWrites(),
                self.y.deferToWrites(),
                self.z.deferToWrites()])

        def second(null):
            d = self.x['a']
            d.addCallback(self.failUnlessEqual, 1)
            d.addCallback(lambda _: self.y['a'])
            d.addCallback(self.failUnlessEqual, 10)
            d.addCallback(lambda _: self.z['a'])
            d.addCallback(self.failUnlessEqual, 100)
            return d

        def third(null):
            def wait():
                d = defer.Deferred()
                reactor.callLater(1.0, d.callback, None)
                return d
            
            def thisOneShutdown(null, objectName):
                print "Done shutting down PDict '%s'" % objectName

            dList = []
            for objectName in ('x', 'y', 'z'):
                d1 = getattr(self, objectName).shutdown()
                if VERBOSE:
                    print "\nAbout to shut down Pdict '%s'" % objectName
                    d1.addCallback(thisOneShutdown, objectName)
                d2 = wait()
                dList.append(defer.DeferredList([d1,d2]))
            return defer.DeferredList(dList)

        self.x = PersistentDict('alpha')
        self.y = PersistentDict('bravo')
        self.z = PersistentDict('charlie')
        
        d = first()
        d.addCallback(second)
        d.addCallback(third)
        return d

    def testThreeSeparatePreloadedDicts(self):
        def first():
            d1 = self.x.preload()
            d2 = self.y.preload()
            d3 = self.z.preload()
            d4 = defer.Deferred()
            reactor.callLater(0.5, d4.callback, None)
            return defer.DeferredList([d1,d2,d3,d4])

        def second(null):
            self.x['a'] = 1
            self.y['a'] = 10
            self.z['a'] = 100
            return defer.DeferredList([
                self.x.deferToWrites(),
                self.y.deferToWrites(),
                self.z.deferToWrites()])

        def third(null):
            self.failUnlessEqual(self.x['a'], 1)
            self.failUnlessEqual(self.y['a'], 10)
            self.failUnlessEqual(self.z['a'], 100)

        def fourth(null):
            def wait():
                d = defer.Deferred()
                reactor.callLater(1.0, d.callback, None)
                return d
            
            def thisOneShutdown(null, objectName):
                print "Done shutting down PDict '%s'" % objectName

            dList = []
            for objectName in ('x', 'y', 'z'):
                d1 = getattr(self, objectName).shutdown()
                if VERBOSE:
                    print "\nAbout to shut down Pdict '%s'" % objectName
                    d1.addCallback(thisOneShutdown, objectName)
                d2 = wait()
                dList.append(defer.DeferredList([d1,d2]))
            return defer.DeferredList(dList)

        self.x = PersistentDict('alpha')
        self.y = PersistentDict('bravo')
        self.z = PersistentDict('charlie')
        
        d = first()
        d.addCallback(second)
        d.addCallback(third)
        d.addCallback(fourth)
        return d

    def testOneDictWithParray(self):
        import sasync.parray as parray
        
        x = PersistentDict('foo')
        y = PersistentArray('bar')
        
        def first():
            x['a'] = 1
            return x.deferToWrites()
        
        def second(null):
            d = x['a']
            d.addCallback(self.failUnlessEqual, 1)
            return d
        
        def third(null):
            return defer.DeferredList([x.shutdown(), y.shutdown()])
        
        d = first()
        d.addCallback(second)
        d.addCallback(third)
        return d

    def testTwoDictsWithParray(self):
        import sasync.parray as parray
        
        x = PersistentDict('foo')
        y = PersistentDict('bar')
        z = PersistentArray('whatever')
        
        def first():
            x['a'] = 1
            y['a'] = 10
            return defer.DeferredList([x.deferToWrites(), y.deferToWrites()])
        
        def second(null):
            d = x['a']
            d.addCallback(self.failUnlessEqual, 1)
            d.addCallback(lambda _: y['a'])
            d.addCallback(self.failUnlessEqual, 10)
            return d
        
        def third(null):
            return defer.DeferredList([
                x.shutdown(), y.shutdown(), z.shutdown()])
        
        d = first()
        d.addCallback(second)
        d.addCallback(third)
        return d


class Pdict:
    def tearDown(self):
        return self.p.shutdown()
    
    def writeToDB(self, **items):
        def _writeToDB(insertionList):
            if VERBOSE:
                print "\nWRITE-TO-DB", insertionList, "\n\n"
            self.pit.sasync_items.insert().execute(*insertionList)
        
        insertionList = []
        for name, value in items.iteritems():
            insertionList.append({'group_id':ID, 'name':name, 'value':value})
        return self.pit.deferToQueue(_writeToDB, insertionList)

    def clearDB(self):
        def _clearDB():
            if VERBOSE:
                print "\nCLEAR-DB\n"
            self.pit.sasync_items.delete(
                self.pit.sasync_items.c.group_id == ID).execute()
        
        return self.pit.deferToQueue(_clearDB)


class PdictNormal(Pdict):
    def setUp(self):
        def started(null):
            self.pit = self.p.i.t
            self.p.data.clear()
            return self.pit.deferToQueue(clear)
        
        def clear():
            si = self.pit.sasync_items
            si.delete(si.c.group_id == ID).execute()

        self.p = PersistentDict(ID)
        d = self.p.i.t.startup()
        d.addCallback(started)
        return d


class TestPdictNormalCore(PdictNormal, TestCase):
    def testSomeWriteSomeSet(self):
        def setStuff(null):
            self.p['b'] = 'beta'
            self.p['d'] = 'delta'
            d = self.p.deferToWrites()
            d.addCallback(lambda _: self.p.items())
            d.addCallback(
                itemsEqual,
                [('a','alpha'), ('b','beta'), ('c','charlie'), ('d','delta')])
            d.addCallback(self.failUnless, "Items not equal")
            return d
        
        d = self.writeToDB(a='alpha', b='bravo', c='charlie')
        d.addCallback(setStuff)
        return d

    def testWriteAndGet(self):
        d = self.writeToDB(a=100, b=200, c='foo')
        d.addCallback(lambda _: self.p['a'])
        d.addCallback(self.failUnlessEqual, 100)
        d.addCallback(lambda _: self.p['b'])
        d.addCallback(self.failUnlessEqual, 200)
        d.addCallback(lambda _: self.p['c'])
        d.addCallback(self.failUnlessEqual, 'foo')
        return d


class TestPdictNormalMain(PdictNormal, TestCase):
    def testLoadAll(self):
        def checkItems(items):
            self.failUnlessEqual(items, {'a':1, 'b':2})
            
        d = self.writeToDB(a=1, b=2)
        d.addCallback(lambda _: self.p.loadAll())
        d.addCallback(checkItems)
        return d

    def testSetAndGet(self):
        self.p['a'] = 10        
        d = self.p.deferToWrites()
        d.addCallback(lambda _: self.p['a'])
        d.addCallback(self.failUnlessEqual, 10)
        return d

    def testSetAndLoadAll(self):
        self.p['a'] = 1
        self.p['b'] = 2

        d = self.p.deferToWrites()
        d.addCallback(lambda _: self.p.loadAll())
        d.addCallback(self.failUnlessEqual, {'a':1, 'b':2})
        return d
            
    def testSetdefaultEmpty(self):
        self.p['a'] = 1
        self.p.writeTracker.put(self.p.setdefault('b', 2))

        d = self.p.deferToWrites()
        d.addCallback(lambda _: self.p.loadAll())
        d.addCallback(self.failUnlessEqual, {'a':1, 'b':2})
        return d

    def testSetClearAndLoadAll(self):
        self.p['a'] = 1
        self.p['b'] = 2
        self.p.clear()
        d = self.p.deferToWrites()
        d.addCallback(lambda _: self.p.loadAll())
        d.addCallback(self.failUnlessEqual, {})
        return d

    def testSetdefaultSet(self):
        self.p['a'] = 1
        self.p.writeTracker.put(self.p.setdefault('a', 2))

        d = self.p.deferToWrites()
        d.addCallback(lambda _: self.p.items())
        d.addCallback(self.failUnlessEqual, [('a',1)])
        return d

    def testSetAndGetComplex(self):
        self.p['a'] = 1
        self.p['b'] = 2
        self.p.writeTracker.put(self.p.setdefault('b', 20))
        self.p.writeTracker.put(self.p.setdefault('c', 3))
        self.p.update({'d':4, 'e':5})

        d = self.p.deferToWrites()
        d.addCallback(lambda _: self.p.items())
        d.addCallback(itemsEqual, [('a',1), ('b',2), ('c',3), ('d',4), ('e',5)])
        d.addCallback(self.failUnless, "Items not equal")
        return d

    def testKeys(self):
        d = self.writeToDB(a=1.1, b=1.2, c=1.3)
        d.addCallback(lambda _: self.p.keys())
        d.addCallback(itemsEqual, ['a', 'b', 'c'])
        d.addCallback(self.failUnless)
        return d

    def testValues(self):
        d = self.writeToDB(a=1.1, b=1.2, c=1.3)
        d.addCallback(lambda _: self.p.values())
        d.addCallback(itemsEqual, [1.1, 1.2, 1.3])
        d.addCallback(self.failUnless)
        return d

    def testItems(self):
        d = self.writeToDB(a=2.1, b=2.2, c=2.3)
        d.addCallback(lambda _: self.p.items())
        d.addCallback(itemsEqual, [('a',2.1), ('b',2.2), ('c',2.3)])
        d.addCallback(self.failUnless)
        return d

    def testContains(self):
        def one(null):
            d = self.p.has_key('a')
            d.addCallback(
                self.failUnless, "Item 'a' should be in the dictionary")
            return d
        
        def another(null):
            d = self.p.has_key('d')
            d.addCallback(self.failIf, "Item 'd' shouldn't be in the dictionary")
            return d
        
        d = self.clearDB()
        d.addCallback(lambda _: self.writeToDB(a=1.1, b=1.2, c=1.3))
        d.addCallback(one)
        d.addCallback(another)
        return d

    def testGetMethod(self):
        d = self.clearDB()
        d.addCallback(lambda _: self.writeToDB(a='present'))
        d.addCallback(lambda _: self.p.get('a', None))
        d.addCallback(self.failUnlessEqual, 'present')
        d.addCallback(lambda _: self.p.get('b', None))
        d.addCallback(self.failUnlessEqual, None)
        return d


class PdictPreload(Pdict):
    def setUp(self):
        def started(null):
            self.pit = self.p.i.t
            self.p.data.clear()
            return self.pit.deferToQueue(clear)
        
        def clear():
            si = self.pit.sasync_items
            si.delete(si.c.group_id == ID).execute()

        self.p = PersistentDict(ID)
        d = self.p.preload()
        d.addCallback(started)
        return d


class TestPdictPreload(PdictPreload, TestCase):
    def testSetAndGet(self):
        self.p['a'] = 10        
        self.failUnlessEqual(self.p['a'], 10)

    def testSetActuallyWrites(self):
        def first(null):
            self.p['a'] = 'new'
            return self.p.deferToWrites()
        def second(null):
            def _second():
                si = self.pit.sasync_items
                row = si.select(
                    SA.and_(
                    si.c.group_id==ID, si.c.name=='a')).execute().fetchone()
                return row['value']
            return self.pit.deferToQueue(_second)
        d = self.clearDB()
        d.addCallback(first)
        d.addCallback(second)
        d.addCallback(self.failUnlessEqual, 'new')
        return d
