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
Unit tests for sasync.items.py.
"""
import random
from twisted.internet.reactor import callLater
from twisted.internet.defer import \
     Deferred, DeferredList, DeferredLock, succeed
from twisted.trial.unittest import TestCase

from sqlalchemy import *

from sasync.database import transact, AccessBroker
import sasync.items as items
import mock

GROUP_ID = 123
VERBOSE = False

db = 'items.db'
    

class TestableItemsTransactor(items.Transactor):
    @transact
    def pre(self):
        # Group 123
        self.sasync_items.insert().execute(
            group_id=123, name='foo', value='OK')
        # Set up an experienced MockThing to have pickled
        thing = mock.MockThing()
        thing.method(1)
        self.sasync_items.insert().execute(
            group_id=123, name='bar', value=thing)
        # Group 124
        self.sasync_items.insert().execute(
            group_id=124, name='foo', value='bogus')
        self.sasync_items.insert().execute(
            group_id=124, name='invalid', value='bogus')

    @transact
    def post(self):
        self.sasync_items.delete().execute()


class ItemsMixin:
    def tearDown(self):
        def _tearDown():
            si = self.i.t.sasync_items
            si.delete(si.c.group_id == GROUP_ID).execute()
        d = self.i.t.deferToQueue(_tearDown, niceness=20)
        d.addCallback(lambda _: self.i.shutdown())
        return d


class TestItemsTransactor(ItemsMixin, TestCase):
    def setUp(self):
        url = "sqlite:///%s" % db
        self.i = items.Items(GROUP_ID, url)
        self.i.t = TestableItemsTransactor(self.i.groupID, url)
        return self.i.t.pre()

    def tearDown(self):
        return self.i.t.post()

    def testLoad(self):
        def gotValue(value, name):
            if name == 'foo':
                self.failUnlessEqual(value, 'OK')
            else:
                self.failUnless(
                    isinstance(value, mock.MockThing),
                    "Item 'bar' is a '%s', not an instance of 'MockThing'" \
                    % value)
                self.failUnless(
                    value.beenThereDoneThat,
                    "Class instance wasn't properly persisted with its state")
                self.failUnlessEqual(
                    value.method(2.5), 5.0,
                    "Class instance wasn't properly persisted with its method")

        dList = []
        for name in ('foo', 'bar'):
            dList.append(self.i.t.load(name).addCallback(gotValue, name))
        return DeferredList(dList)

    def testLoad(self):
        def gotValue(value, name):
            if name == 'foo':
                self.failUnlessEqual(value, 'OK')
            else:
                self.failUnless(
                    isinstance(value, mock.MockThing),
                    "Item 'bar' is a '%s', not an instance of 'MockThing'" \
                    % value)
                self.failUnless(
                    value.beenThereDoneThat,
                    "Class instance wasn't properly persisted with its state")
                self.failUnlessEqual(
                    value.method(2.5), 5.0,
                    "Class instance wasn't properly persisted with its method")

        dList = []
        for name in ('foo', 'bar'):
            dList.append(self.i.t.load(name).addCallback(gotValue, name))
        return DeferredList(dList)

    def testLoadAbsent(self):
        def gotValue(value):
            self.failUnless(
                isinstance(value, items.Missing),
                "Should have returned 'Missing' object, not '%s'!" % \
                str(value))
        def gotExpectedError(failure):
            self.fail("Shouldn't have raised error on missing value")
        return self.i.t.load('invalid').addCallbacks(
            gotValue, gotExpectedError)

    def testLoadAll(self):
        def loaded(items):
            itemKeys = items.keys()
            itemKeys.sort()
            self.failUnlessEqual(itemKeys, ['bar', 'foo'])
        return self.i.t.loadAll().addCallback(loaded)

    def insertLots(self, callback):
        noviceThing = mock.MockThing()
        experiencedThing = mock.MockThing()
        experiencedThing.method(0)
        self.whatToInsert = {
            'alpha':5937341,
            'bravo':'abc',
            'charlie':-3.1415,
            'delta':(1,2,3),
            'echo':True,
            'foxtrot':False,
            'golf':noviceThing,
            'hotel':experiencedThing,
            'india':mock.MockThing
            }
        dList = []
        for name, value in self.whatToInsert.iteritems():
            dList.append(self.i.t.insert(name, value))
        return DeferredList(dList).addCallback(
            callback, self.whatToInsert.copy())

    def testInsert(self):
        def done(null, items):
            def check():
                table = self.i.t.sasync_items
                for name, inserted in items.iteritems():
                    value = table.select(
                        and_(table.c.group_id == 123,
                             table.c.name == name)
                        ).execute().fetchone()['value']
                    self.failUnlessEqual(
                        value, inserted,
                        "Inserted '%s:%s' but read '%s' back from the database!" % \
                        (name, inserted, value))
                    for otherName, otherValue in items.iteritems():
                        if otherName != name and value == otherValue:
                            self.fail(
                                "Inserted item '%s' is equal to item '%s'" % \
                                (name, otherName))
            return self.i.t.deferToQueue(check)
        return self.insertLots(done)

    def testDeleteOne(self):
        def gotOriginal(value):
            self.failUnlessEqual(value, 'OK')
            return self.i.t.delete('foo').addCallback(getAfterDeleted)
        def getAfterDeleted(null):
            return self.i.t.load('foo').addCallback(checkIfDeleted)
        def checkIfDeleted(value):
            self.failUnless(isinstance(value, items.Missing))
        return self.i.t.load('foo').addCallback(gotOriginal)

    def testDeleteMultiple(self):
        def getAfterDeleted(null):
            return self.i.t.loadAll().addCallback(checkIfDeleted)
        def checkIfDeleted(values):
            self.failUnlessEqual(values, {})
        return self.i.t.delete('foo', 'bar').addCallback(getAfterDeleted)

    def testNamesFew(self):
        def got(names):
            names.sort()
            self.failUnlessEqual(names, ['bar', 'foo'])
        return self.i.t.names().addCallback(got)

    def testNamesMany(self):
        def get(null, items):
            return self.i.t.names().addCallback(got, items.keys())
        def got(names, shouldHave):
            shouldHave += ['foo', 'bar']
            names.sort()
            shouldHave.sort()
            self.failUnlessEqual(names, shouldHave)
        return self.insertLots(get)

    def testUpdate(self):
        def update(null, items):
            return DeferredList([
                self.i.t.update('alpha',   1),
                self.i.t.update('bravo',   2),
                self.i.t.update('charlie', 3)
                ]).addCallback(check, items)
        def check(null, items):
            return self.i.t.loadAll().addCallback(loaded, items)
        def loaded(loadedItems, controlItems):
            controlItems.update({'alpha':1, 'bravo':2, 'charlie':3})
            for name, value in controlItems.iteritems():
                self.failUnlessEqual(
                    value, loadedItems.get(name, 'Impossible Value'))
        return self.insertLots(update)

    
class TestItems(ItemsMixin, TestCase):
    def setUp(self):
        self.i = items.Items(GROUP_ID, "sqlite:///%s" % db)
    
    def testInsertAndLoad(self):
        nouns = ('lamp', 'rug', 'chair')
        def first(null):
            return self.i.loadAll().addCallback(second)
        def second(items):
            self.failUnlessEqual(items['Nouns'], nouns)
        return self.i.insert('Nouns', nouns).addCallback(first)

    def testInsertAndDelete(self):
        items = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4}

        def first(null):
            return self.i.delete('c').addCallback(second)

        def second(null):
            return self.i.names().addCallback(third)

        def third(nameList):
            desiredList = [x for x in items.keys() if x != 'c']
            desiredList.sort()
            nameList.sort()
            self.failUnlessEqual(nameList, desiredList)

        dL = []
        for name, value in items.iteritems():
            dL.append(self.i.insert(name, value))
        return DeferredList(dL).addCallback(first)

    def testInsertAndLoadAll(self):
        items = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4}
        def first(null):
            return self.i.loadAll().addCallback(second)
        def second(loadedItems):
            self.failUnlessEqual(loadedItems, items)

        dL = []
        for name, value in items.iteritems():
            dL.append(self.i.insert(name, value))
        return DeferredList(dL).addCallback(first)

    def testInsertAndUpdate(self):
        items = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4}
        def first(null):
            return self.i.update('b', 10).addCallback(second)
        def second(null):
            return self.i.loadAll().addCallback(third)
        def third(loadedItems):
            expectedItems = {'a':0, 'b':10, 'c':2, 'd':3, 'e':4}
            self.failUnlessEqual(loadedItems, expectedItems)

        dL = []
        for name, value in items.iteritems():
            dL.append(self.i.insert(name, value))
        return DeferredList(dL).addCallback(first)


class TestItemsIntegerNames(ItemsMixin, TestCase):
    def setUp(self):
        self.items = {'1':'a', 2:'b', 3:'c', '04':'d'}
        self.i = items.Items(GROUP_ID, "sqlite:///%s" % db, nameType=int)

    def insertStuff(self):
        dL = []
        for name, value in self.items.iteritems():
            dL.append(self.i.insert(name, value))
        return DeferredList(dL)

    def testNames(self):
        def first(null):
            return self.i.names().addCallback(second)
        def second(names):
            names.sort()
            self.failUnlessEqual(names, [1, 2, 3, 4])
        return self.insertStuff().addCallback(first)

    def testLoadAll(self):
        def first(null):
            return self.i.loadAll().addCallback(second)
        def second(loaded):
            self.failUnlessEqual(loaded, {1:'a', 2:'b', 3:'c', 4:'d'})
        return self.insertStuff().addCallback(first)


class TestItemsStringNames(ItemsMixin, TestCase):
    def setUp(self):
        self.items = {'1':'a', 2:'b', u'3':'c', "4":'d'}
        self.i = items.Items(GROUP_ID, "sqlite:///%s" % db, nameType=str)

    def insertStuff(self):
        dL = []
        for name, value in self.items.iteritems():
            dL.append(self.i.insert(name, value))
        return DeferredList(dL)

    def testNames(self):
        def first(null):
            return self.i.names().addCallback(second)
        def second(names):
            names.sort()
            self.failUnlessEqual(names, ['1', '2', '3', '4'])
        return self.insertStuff().addCallback(first)        

    def testLoadAll(self):
        def first(null):
            return self.i.loadAll().addCallback(second)
        def second(loaded):
            self.failUnlessEqual(loaded, {'1':'a', '2':'b', '3':'c', '4':'d'})
        return self.insertStuff().addCallback(first)
        

