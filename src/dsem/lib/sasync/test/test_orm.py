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
Unit tests for ORM aspects of sasync.database.py.
"""

from twisted.internet import reactor, defer
from twisted.trial.unittest import TestCase

import sqlalchemy as SA
from sqlalchemy.orm import mapper, relation

from sasync.database import AccessBroker, transact


VERBOSE = False

DELAY = 0.5
DB_URL = 'sqlite:///database.db'

# DEBUG
if VERBOSE:
    import logging
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)


def deferToDelay(result, delay=0.1):
    d = defer.Deferred()
    reactor.callLater(delay, d.callback, result)
    return d


class User(object):
    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password


class Address(object):
    def __init__(self, street, city, state, zip):
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip


class ObjectBroker(AccessBroker):
    """
    From the example at U{http://www.sqlalchemy.org/docs/datamapping.myt}
    """
    def __getattribute__(self, name):
        # For debugging, to see what session is stored
        result = AccessBroker.__getattribute__(self, name)
        if VERBOSE and name == 'session':
            print "SESSION:", result
        return result

    def startup(self):
        def gotTables(null):
            r = relation(
                Address, backref='user', cascade="all, delete, delete-orphan")
            mapper(User, self.users, properties={'addresses':r})
            mapper(Address, self.addresses)
        
        d = self.table(
            'users',
            SA.Column('user_id', SA.Integer, primary_key=True),
            SA.Column('user_name', SA.String(16)),
            SA.Column('password', SA.String(20))
            )
        d.addCallback(lambda _: self.table(
            'addresses',
            SA.Column('address_id', SA.Integer, primary_key=True),
            SA.Column('user_id', SA.Integer, SA.ForeignKey("users.user_id")),
            SA.Column('street', SA.String(100)),
            SA.Column('city', SA.String(80)),
            SA.Column('state', SA.String(2)),
            SA.Column('zip', SA.String(10))
            ))
        d.addCallback(gotTables)
        return d

    @transact
    def clear(self):
        for obj in self.session:
            self.session.delete(obj)
    
    @transact
    def setJane(self):
        u = User('jane', 'hihilala')
        u.addresses.append(
            Address('123 anywhere street', 'big city', 'UT', '76543'))
        u.addresses.append(
            Address('1 Park Place', 'some other city', 'OK', '83923'))
        self.session.save(u)

    @transact
    def setTarzan(self):
        u = User('tarzan', 'ugh')
        u.addresses.append(
            Address('234 another street', 'big city', 'UT', '76543'))
        u.addresses.append(
            Address('345 Zoo Circle', 'New York', 'NY', '32145'))
        self.session.save(u)

    @transact
    def getResidents(self, state):
        users = self.session.query(User).join('addresses').filter_by(state=state)
        return [x.user_name for x in users]
    
    @transact
    def getTarzan(self):
        return self.session.query(User).filter_by(user_name='tarzan').one()
    
    @transact
    def getJane(self):
        return self.session.query(User).filter_by(user_name='jane').one()
    
    @transact
    def deleteUser(self, user):
        self.session.delete(user)


class TestORM(TestCase):
    def setUp(self):
        self.broker = ObjectBroker(DB_URL)

    def tearDown(self):
        def cleared(null):
            self.broker.session.close()
            SA.orm.clear_mappers()
            
        d = self.broker.clear(session=True)
        d.addCallback(cleared)
        return d
    
    def test_query_bothStates(self):
        d = self.broker.setJane(session=True)
        d = self.broker.setTarzan(session=True)
        d.addCallback(lambda _: self.broker.getResidents('UT', session=True))
        d.addCallback(self.failUnlessEqual, ['jane', 'tarzan'])
        return d

    def test_query_oneState(self):
        d = self.broker.setJane(session=True)
        d = self.broker.setTarzan(session=True)
        d.addCallback(lambda _: self.broker.getResidents('OK', session=True))
        d.addCallback(self.failUnlessEqual, ['jane'])
        return d

    def testRepeatedQueries(self):
        d = self.broker.setJane(session=True)
        d = self.broker.setTarzan(session=True)
        d.addCallback(lambda _: self.broker.getResidents('UT', session=True))
        d.addCallback(self.failUnlessEqual, ['jane', 'tarzan'])
        d.addCallback(lambda _: self.broker.getResidents('OK', session=True))
        d.addCallback(self.failUnlessEqual, ['jane'])
        return d

    @defer.deferredGenerator
    def testDeleteUser(self):
        # Setup Tarzan & Jane
        wfd = defer.waitForDeferred(self.broker.setJane(session=True))
        yield wfd; wfd.getResult()
        wfd = defer.waitForDeferred(self.broker.setTarzan(session=True))
        yield wfd; wfd.getResult()
        # Delete Jane
        wfd = defer.waitForDeferred(self.broker.getJane(session=True))
        yield wfd
        user = wfd.getResult()
        wfd = defer.waitForDeferred(self.broker.deleteUser(user, session=True))
        yield wfd; wfd.getResult()
        # Make sure only Tarzan is listed for a Utah address
        wfd = defer.waitForDeferred(self.broker.getResidents('UT', session=True))
        yield wfd
        self.failUnlessEqual(wfd.getResult(), ['tarzan'])
