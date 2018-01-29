# sAsync:
# An enhancement to the SQLAlchemy package that provides persistent
# dictionaries, text indexing and searching, and an access broker for
# conveniently managing database access, table setup, and
# transactions. Everything can be run in an asynchronous fashion using the
# Twisted framework and its deferred processing capabilities.
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
Persistent Three-dimensional array objects
"""

# Imports
from twisted.internet import defer
import sqlalchemy as SA

from database import transact, AccessBroker
import search


NICENESS_WRITE = 6


class Transactor(AccessBroker):
    """
    I do the hands-on work of (potentially) non-blocking database access for
    the persistence of array elements within a uniquely-identified group.

    My methods return Twisted deferred instances to the results of their
    database accesses rather than forcing the client code to block while the
    database access is being completed.
    
    """
    def __init__(self, ID, *url, **kw):
        """
        Instantiates me for a three-dimensional array of elements within a
        particular group uniquely identified by the supplied integer I{ID},
        using a database connection to I{url}.
        """
        if not isinstance(ID, int):
            raise TypeError("Item IDs must be integers")
        self.groupID = ID
        if url:
            super(Transactor, self).__init__(url[0], **kw)
        else:
            super(Transactor, self).__init__()

    def startup(self):
        """
        You can run my transaction methods when the deferred returned from
        this method fires, and not before.
        """
        d = self.table(
            'sasync_array',
            SA.Column('group_id', SA.Integer),
            SA.Column('x', SA.Integer),
            SA.Column('y', SA.Integer),
            SA.Column('z', SA.Integer),
            SA.Column('value', SA.PickleType, nullable=False),
            unique_elements=['group_id', 'x', 'y', 'z']
            )
        return d
    
    @transact
    def load(self, x, y, z):
        """
        Element load transaction
        """
        array = self.sasync_array
        if not self.s('load'):
            self.s(
                [array.c.value],
                SA.and_(array.c.group_id == self.groupID,
                        array.c.x == SA.bindparam('x'),
                        array.c.y == SA.bindparam('y'),
                        array.c.z == SA.bindparam('z'))
                )
        rows = self.s().execute(x=hash(x), y=hash(y), z=hash(z)).fetchone()
        if not rows:
            return None
        else:
            return rows['value']

    @transact
    def update(self, x, y, z, value):
        """
        Element overwrite (entry update) transaction
        """
        elements = self.sasync_array
        u = elements.update(
            SA.and_(elements.c.group_id == self.groupID,
                    elements.c.x == hash(x),
                    elements.c.y == hash(y),
                    elements.c.z == hash(z))
            )
        u.execute(value=value)

    @transact
    def insert(self, x, y, z, value):
        """
        Element add (entry insert) transaction
        """
        self.sasync_array.insert().execute(
            group_id=self.groupID,
            x=hash(x), y=hash(y), z=hash(z), value=value)

    @transact
    def delete(self, x, y, z):
        """
        Element delete transaction
        """
        elements = self.sasync_array
        self.sasync_array.delete(
            SA.and_(elements.c.group_id == self.groupID,
                    elements.c.x == hash(x),
                    elements.c.y == hash(y),
                    elements.c.z == hash(z))
            ).execute()

    @transact
    def clear(self):
        """
        Transaction to clear all elements (B{Use with care!})
        """
        elements = self.sasync_array
        self.sasync_array.delete(
            elements.c.group_id == self.groupID).execute()


class PersistentArray(object):
    """
    I am a three-dimensional array of Python objects, addressable by any
    three-way combination of hashable Python objects. You can use me as a
    two-dimensional array by simply using some constant, e.g., C{None} when
    supplying an address for my third dimension.

    B{IMPORTANT}: Make sure you call my L{shutdown} method for an instance of
    me that you're done with before allowing that instance to be deleted.
    """
    search = None

    def __init__(self, ID, *url, **kw):
        """
        Constructor, with a URL and any engine-specifying keywords supplied if
        a particular engine is to be used for this instance. The following
        additional keyword is particular to this constructor:
        
        @keyword search: Set C{True} if text indexing is to be performed on items
            as they are written.

        """
        try:
            self.ID = hash(ID)
        except:
            raise TypeError("Item IDs must be hashable")
        if kw.pop('search', False):
            # No search object, worry about searching later
            self.search = None
        if url:
            self.t = Transactor(self.ID, url[0], **kw)
        else:
            self.t = Transactor(self.ID)
    
    def shutdown(self, *null):
        """
        Shuts down my database L{Transactor} and its synchronous task queue.
        """
        return self.t.shutdown()

    def write(self, funcName, *args, **kw):
        """
        Performs a database write transaction, returning a deferred to its
        completion.

        If we are updating the search index, there's a nuance to the
        deferred processing. In that case, when the write is done, the
        deferred is fired and processing separately proceeds with indexing
        of the written value. Here's how it works:

            1. Create a clean deferred B{d1} to return to the caller, whose
               callback(s) will be fired from the callback to the transaction's
               own deferred B{d2}.

            2. Start the write transaction and assign the C{writeDone} function
               as the callback to its deferred B{d2}. Note that the
               defer-to-queue transaction keeps a reference to the deferred
               object it instantiates, so we don't have to do so for either
               B{d2} or B{d3}. Those references are merely defined in the
               method for code readability.

        """
        def writeDone(noneResult, d1):
            x, y, z = [hash(arg) for arg in args[0:3]]
            document = "%d-%d" % (self.groupID, x)
            section = "%d-%d" % (y, z)
            d3 = self.search.index(
                value, document=document, section=section)
            d3.addCallback(self.search.ready)
            d1.callback(None)
        
        func = getattr(self.t, funcName)
        kwNew = {'niceness':kw['niceness']}
        if self.search is None:
            return func(*args, **kwNew)
        else:        
            d1 = defer.Deferred()
            self.search.busy()
            d2 = func(*args, **kwNew)
            d2.addCallback(writeDone, d1)
            return d1

    def get(self, x, y, z):
        """
        Retrieves an element (x,y,z) from the database.
        """
        d = self.t.dt.deferToAll()
        d.addCallback(lambda _: self.t.load(x, y, z))
        return d

    def set(self, x, y, z, value):
        """
        Persists the supplied I{value} of element (x,y,z) to the database,
        inserting or updating a row as appropriate.
        """
        def loaded(loadedValue):
            if loadedValue is None:
                return self.write(
                    "insert", x, y, z, value, niceness=NICENESS_WRITE)
            else:
                return self.write(
                    "update", x, y, z, value, niceness=NICENESS_WRITE)
        
        d = self.t.load(x, y, z)
        d.addCallback(loaded)
        self.t.dt.put(d)
        return d

    def delete(self, x, y, z):
        """
        Deletes the database row for element (x,y,z).
        """
        d = self.write("delete", x, y, z, niceness=NICENESS_WRITE)
        self.t.dt.put(d)
        return d

    def clear(self):
        """
        Deletes the entire group of database rows for U{all} of my elements
        (B{Use with care!})
        """
        d =self.write("clear", niceness=0)
        self.t.dt.put(d)
        return d


__all__ = ['PersistentArray']
