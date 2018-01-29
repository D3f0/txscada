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
Dictionary-like objects with behind-the-scenes database persistence

"""

# Imports
from twisted.internet import defer
import sqlalchemy as SA

from database import transact, AccessBroker
import search


NICENESS_WRITE = 6


class Missing:
    """
    An instance of me is returned as the value of a missing item.
    """
    def __init__(self, group, name):
        self.group, self.name = group, name


class Transactor(AccessBroker):
    """
    I do the hands-on work of non-blocking database access for the persistence
    of name:value items within a uniquely-identified group, e.g., for a
    persistent dictionary using L{PersistentDict}.

    My methods return Twisted deferred instances to the results of their
    database accesses rather than forcing the client code to block while the
    database access is being completed.
    
    """
    def __init__(self, ID, *url, **kw):
        """
        Instantiates me for the items of a particular group uniquely identified
        by the supplied integer I{ID}, optionally using a particular database
        connection to I{url} with any supplied keywords.
        """
        if not isinstance(ID, int):
            raise TypeError("Item IDs must be integers")
        self.groupID = ID
        if url:
            AccessBroker.__init__(self, url[0], **kw)
        else:
            AccessBroker.__init__(self)
    
    def startup(self):
        """
        Startup method, automatically called before the first transaction.
        """
        return self.table(
            'sasync_items',
            SA.Column('group_id', SA.Integer, primary_key=True),
            SA.Column('name', SA.String(40), primary_key=True),
            SA.Column('value', SA.PickleType, nullable=False)
            )
    
    @transact
    def load(self, name):
        """
        Item load transaction
        """
        items = self.sasync_items
        if not self.s('load'):
            self.s(
                [items.c.value],
                SA.and_(items.c.group_id == self.groupID,
                        items.c.name == SA.bindparam('name')))
        row = self.s().execute(name=name).fetchone()
        if not row:
            return Missing(self.groupID, name)
        else:
            return row['value']
    
    @transact
    def loadAll(self):
        """
        Load all my items, returing a name:value dict
        """
        items = self.sasync_items
        if not self.s('load_all'):
            self.s(
                [items.c.name, items.c.value],
                items.c.group_id == self.groupID)
        rows = self.s().execute().fetchall()
        result = {}
        for row in rows:
            result[row['name']] = row['value']
        return result

    @transact
    def update(self, name, value):
        """
        Item overwrite (entry update) transaction
        """
        items = self.sasync_items
        u = items.update(
            SA.and_(items.c.group_id == self.groupID,
                    items.c.name == name))
        u.execute(value=value)
    
    @transact
    def insert(self, name, value):
        """
        Item add (entry insert) transaction
        """
        self.sasync_items.insert().execute(
            group_id=self.groupID, name=name, value=value)

    @transact
    def delete(self, *names):
        """
        Item(s) delete transaction
        """
        items = self.sasync_items
        self.sasync_items.delete(
            SA.and_(items.c.group_id == self.groupID,
                    items.c.name.in_(names))).execute()
    
    @transact
    def names(self):
        """
        All item names loading transaction
        """
        items = self.sasync_items
        if not self.s('names'):
            self.s(
                [items.c.name],
                items.c.group_id == self.groupID)
        return [str(x[0]) for x in self.s().execute().fetchall()]


class Items(object):
    """
    I provide a public interface for non-blocking database access to
    persistently stored name:value items within a uniquely-identified group,
    e.g., for a persistent dictionary using L{PersistentDict}.

    Before you use any instance of me, you must specify the parameters for
    creating an SQLAlchemy database engine. A single argument is used, which
    specifies a connection to a database via an RFC-1738 url. In addition, the
    following keyword options can be employed, which are listed in the API docs
    for L{sasync} and L{sasync.database.AccessBroker}.

    You can set an engine globally, for all instances of me via the
    L{sasync.engine} package-level function, or via the L{AccessBroker.engine}
    class method. Alternatively, you can specify an engine for one particular
    instance by supplying the parameters to my constructor.
    
    B{IMPORTANT}: Make sure you call my L{shutdown} method for an instance of
    me that you're done with before allowing that instance to be deleted.
    """
    search = None
    
    def __init__(self, ID, *url, **kw):
        """
        Instantiates me for the items of a particular group uniquely identified
        by the supplied hashable I{ID}. Ensures that I have access to a
        class-wide instance of a L{Search} object so that I can update the
        database's full-text index when writing values containing text content.

        In addition to any engine-specifying keywords supplied, the following
        are particular to this constructor:

        @param ID: A hashable object that is used as my unique identifier.

        @keyword nameType: A C{type} object defining the type that each name
            will be coerced to after being loaded as a string from the
            database.

        @keyword search: Set C{True} if text indexing is to be performed on items
            as they are written.

        """
        try:
            self.groupID = hash(ID)
        except:
            raise TypeError("Item IDs must be hashable")
        if kw.pop('search', False):
            # No search object, worry about searching later
            self.search = None
        self.nameType = kw.pop('nameType', str)
        if url:
            self.t = Transactor(self.groupID, url[0], **kw)
        else:
            self.t = Transactor(self.groupID)

    def shutdown(self, *null):
        """
        Shuts down my database L{Transactor} and its synchronous task queue.
        """
        return self.t.shutdown()

    def write(self, funcName, name, value, niceness=0):
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
            object it instantiates, so we don't have to do so for either B{d2}
            or B{d3}. Those references are merely defined in the method for
            code readability.

        """
        def writeDone(noneResult, d1):
            d3 = self.search.index(
                value, document=self.groupID, section=hash(name))
            d3.addCallback(self.search.ready)
            d1.callback(None)

        func = getattr(self.t, funcName)
        if self.search is None:
            return func(name, value, niceness=niceness)
        else:        
            d1 = defer.Deferred()
            self.search.busy()
            d2 = func(name, value, niceness=niceness)
            d2.addCallback(writeDone, d1)
            return d1
    
    def load(self, name):
        """
        Loads item I{name} from the database, returning a deferred to the
        loaded value. A L{Missing} object represents the value of a missing
        item.
        """
        return self.t.load(name)
    
    def loadAll(self):
        """
        Loads all items in my group from the database, returning a deferred
        to a dict of the loaded values. The keys of the dict are coerced to the
        type of my I{nameType} attribute.
        """
        def loaded(valueDict):
            newDict = {}
            for name, value in valueDict.iteritems():
                key = self.nameType(name)
                newDict[key] = value
            return newDict
        
        d = self.t.loadAll()
        d.addCallback(loaded)
        return d
    
    def update(self, name, value):
        """
        Updates the database entry for item I{name} = I{value}, returning a
        deferred that fires when the transaction is done.
        """
        return self.write('update', name, value, niceness=NICENESS_WRITE)
    
    def insert(self, name, value):
        """
        Inserts a database entry for item I{name} = I{value}, returning a
        deferred that fires when the transaction is done.
        """
        return self.write('insert', name, value, niceness=NICENESS_WRITE)
    
    def delete(self, *names):
        """
        Deletes the database entries for the items having the supplied
        I{*names}, returning a deferred that fires when the transaction is
        done.

        If we are updating the search index, there's a nuance to the
        deferred processing. In that case, when the deletions are done, the
        deferred is fired and processing separately proceeds with dropping
        index entries for the deleted values. Here's how it works:

            1. Create a clean deferred B{d1} to return to the caller, whose
            callback(s) will be fired from the callback to the transaction's
            own deferred B{d2}.

            2. Start the delete transaction and assign the C{deleteDone}
            function as the callback to its deferred B{d2}. Note that the
            defer-to-thread transaction keeps a reference to the deferred
            object it instantiates, so we don't have to do so for either B{d2}
            or B{d3}. Those references are merely defined in the method for
            code readability.

        """
        def deleteDone(noneResult, d1):
            dList = []
            for name in names:
                dList.append(search.drop(
                    document=self.groupID, section=hash(name)))
            d3 = defer.DeferredList(dList)
            d3.addCallback(self.search.ready)
            d1.callback(None)

        kw = {'niceness':NICENESS_WRITE}
        if self.search is None:
            return self.t.delete(*names, **kw)
        else:        
            d1 = defer.Deferred()
            self.search.busy()
            d2 = self.t.delete(*names, **kw)
            d2.addCallback(deleteDone, d1)
            return d1
    
    def names(self):
        """
        Returns a deferred that fires with a list of the names of all items
        currently defined in my group.
        """
        def gotNames(names):
            return [self.nameType(x) for x in names]
        
        d = self.t.names()
        d.addCallback(gotNames)
        return d


__all__ = ['Missing', 'Items']
