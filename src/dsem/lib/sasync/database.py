# sAsync:
# An enhancement to the SQLAlchemy package that provides persistent
# dictionaries, text indexing and searching, and an access broker for
# conveniently managing database access, table setup, and
# transactions. Everything is run in an asynchronous fashion using the Twisted
# framework and its deferred processing capabilities.
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
Asynchronous database transactions via SQLAlchemy.
"""

import sys
from twisted.internet import defer
from twisted.python import failure

import sqlalchemy as SA

######################################################################
# SA 0.4 support contributed by Ricky Iacovou,  based upon:
#
#   http://www.sqlalchemy.org/docs/04/intro.html#overview_migration
#
# Determine the version of SQLAlchemy used, 0.3 or 0.4, and set the
# Boolean variable "SA04" accordingly.
#
# We could also use a capability-based approach, like:
#
# try:
#     MetaData = SA.BoundMetaData
# except AttributeError:
#     MetaData = SA.MetaData
#
# However, late 0.3.x versions also supported some 0.4 constructs,
# so better use an explicit 0.3.x -> 0.4.x cutoff in order to avoid
# ambiguity.
######################################################################
_sv = SA.__version__.split ('.')
try:
    _v = int (_sv[0]) + (int(_sv[1]) / 10.0)
except:
    # Not strictly an Import Error, but close enough.
    raise ImportError("Failed to determine SQLAlchemy version: %s", _sv)
if _v >= 0.4:
    SA04 = True
else:
    SA04 = False
del _sv, _v
# End of version check


from asynqueue import ThreadQueue

import misc


class DatabaseError(Exception):
    """
    A problem occured when trying to access the database.
    """


def transact(f):
    """
    Use this function as a decorator to wrap the supplied method I{f} of
    L{AccessBroker} in a transaction that runs C{f(*args, **kw)} in its own
    transaction.

    Immediately returns an instance of L{twisted.internet.defer.Deferred} that
    will eventually have its callback called with the result of the
    transaction. Inspired by and largely copied from Valentino Volonghi's
    C{makeTransactWith} code.

    You can add the following keyword options to your function call:

    @keyword niceness: Scheduling niceness, an integer between -20 and 20,
      with lower numbers having higher scheduling priority as in UNIX C{nice}
      and C{renice}.

    @keyword doNext: Set C{True} to assign highest possible priority, even
      higher than with niceness = -20.                

    @keyword doLast: Set C{True} to assign lower possible priority, even
      lower than with niceness = 20.

    @keyword session: Set this option to C{True} to get a I{session} attribute
      for use within the transaction, which will be flushed at the end of the
      transaction.

    @type session: Boolean option, default C{False}

    @keyword ignore: Set this option to C{True} to have errors in the
      transaction function ignored and just do the rollback quietly.

    @type ignore: Boolean option, default C{False}
    
    """
    def substituteFunction(self, *args, **kw):
        """
        Puts the original function in the synchronous task queue and returns a
        deferred to its result when it is eventually run.

        This function will be given the same name as the original function so
        that it can be asked to masquerade as the original function. As a
        result, the threaded call to the original function that it makes inside
        its C{transaction} sub-function will be able to use the arguments for
        that original function. (The caller will actually be calling this
        substitute function, but it won't know that.)

        The original function should be a method of a L{AccessBroker} subclass
        instance, and the queue for that instance will be used to run it.
        """
        def transaction(usingSession, func, *t_args, **t_kw):
            """
            Everything making up a transaction, and everything run in the
            thread, is contained within this little function, including of
            course a call to C{func}.
            """
            if not usingSession:
                trans = self.connection.begin()
            if not hasattr(func, 'im_self'):
                t_args = (self,) + t_args
            try:
                result = func(*t_args, **t_kw)
            except Exception, e:
                if not usingSession:
                    trans.rollback()
                if not ignore:
                    raise e
            else:
                if usingSession:
                    self.session.flush()
                else:
                    trans.commit()
                return result
            return failure.Failure()

        def doTransaction(usingSession):
            """
            Queues up the transaction and immediately returns a deferred to
            its eventual result.
            """
            if isNested():
                return f(self, *args, **kw)
            return self.q.call(transaction, usingSession, f, *args, **kw)

        def started(null):
            self.ranStart = True
            del self._transactionStartupDeferred
            if useSession:
                d = self.getSession()
            else:
                d = self.connect()
            d.addCallback(lambda _: self.q.call(
                transaction, False, self.first, doNext=True))
            return d

        def isNested():
            frame = sys._getframe()
            while True:
                frame = frame.f_back
                if frame is None:
                    return False
                if frame.f_code == transaction.func_code:
                    return True

        ignore = kw.pop('ignore', False)
        useSession = kw.pop('session', False)
        if hasattr(self, 'connection') and getattr(self, 'ranStart', False):
            # We already have a connection, let's get right to the transaction
            if useSession:
                d = self.getSession()
                d.addCallback(lambda _: doTransaction(True))
            else:
                d = doTransaction(False)
        elif hasattr(self, '_transactionStartupDeferred') and \
             not self._transactionStartupDeferred.called:
            # Startup is in progress, make a new Deferred to the start of the
            # transaction and chain it to the startup Deferred.
            d = defer.Deferred()
            if useSession:
                d.addCallback(lambda _: self.getSession())
            d.addCallback(lambda _: doTransaction(useSession))
            self._transactionStartupDeferred.chainDeferred(d)
        else:
            # We need to start things up before doing this first transaction
            d = defer.maybeDeferred(self.startup)
            self._transactionStartupDeferred = d
            d.addCallback(started)
            d.addCallback(lambda _: doTransaction(useSession))
        # Return whatever Deferred we've got
        return d

    if f.func_name == 'first':
        return f
    substituteFunction.func_name = f.func_name
    return substituteFunction


class AccessBroker(object):
    """
    I manage asynchronous access to a database.

    Before you use any instance of me, you must specify the parameters for
    creating an SQLAlchemy database engine. A single argument is used, which
    specifies a connection to a database via an RFC-1738 url. In addition, the
    following keyword options can be employed, which are listed below with
    their default values.

    You can set an engine globally, for all instances of me via the
    L{sasync.engine} package-level function, or via my L{engine} class
    method. Alternatively, you can specify an engine for one particular
    instance by supplying the parameters to the constructor.
          
    SQLAlchemy has excellent documentation, which describes the engine
    parameters in plenty of detail. See
    U{http://www.sqlalchemy.org/docs/dbengine.myt}.

    @ivar dt: A property-generated reference to a deferred tracker that you can
      use to wait for database writes. See L{misc.DeferredTracker}.

    @ivar q: A property-generated reference to a threaded task queue that is
      dedicated to my database connection.

    @ivar connection: The current SQLAlchemy connection object, if
      any yet exists. Generated by my L{connect} method.
    
    """
    globalParams = ('', {})
    queues = {}
    
    def __init__(self, *url, **kw):
        """
        Constructs an instance of me, optionally specifying parameters for an
        SQLAlchemy engine object that serves this instance only.
        """
        self.selects = {}
        if url:
            self.engineParams = (url[0], kw)
        else:
            self.engineParams = self.globalParams
        self.running = False

    @classmethod
    def engine(cls, url, **kw):
        """
        Sets default connection parameters for all instances of me.
        """
        cls.globalParams = (url, kw)

    def _getDeferredTracker(self):
        """
        Returns an instance of L{misc.DeferredTracker} that is dedicated to the
        bound method's instance of me. Creates the deferred tracker the first
        time this method is called for a given instance of me.
        """
        if not hasattr(self, '_deferredTracker'):
            self._deferredTracker = misc.DeferredTracker()
        return self._deferredTracker
    dt = property(_getDeferredTracker)

    def _getQueue(self):
        """
        Returns a threaded task queue that is dedicated to my database
        connection. Creates the queue the first time the property is accessed.
        """
        def newQueue():
            queue = ThreadQueue(1)
            self.running = True
            self.queues[key] = queue
            return queue

        if hasattr(self, '_currentQueue'):
            return self._currentQueue
        url, kw = self.engineParams
        key = hash((url,) + tuple(kw.items()))
        if key in self.queues:
            queue = self.queues[key]
            if not queue.isRunning():
                queue = newQueue()
        else:
            queue = newQueue()
        self._currentQueue = queue
        return queue

    q = property(_getQueue, doc="""
    Accessing the 'q' attribute will always return a running queue object that
    is dedicated to this instance's connection parameters
    """)

    def connect(self, forceNew=False):
        """
        Generates and returns a singleton connection object.
        """
        def getEngine():
            if hasattr(self, '_dEngine'):
                d = defer.Deferred()
                d.addCallback(lambda _: getConnection())
                self._dEngine.chainDeferred(d)
            else:
                d = self._dEngine = \
                    self.q.call(createEngine, doNext=True)
                d.addCallback(gotEngine)
            return d

        def createEngine():
            url, kw = self.engineParams
            # The 'threadlocal' keyword value is unchanged from SA 0.3 to 0.4
            kw['strategy'] = 'threadlocal'
            return SA.create_engine(url, **kw)
        
        def gotEngine(engine):
            del self._dEngine
            self._engine = engine
            return getConnection()

        def getConnection():
            if not forceNew and hasattr(self, 'connection'):
                d = defer.succeed(self.connection)
            elif not forceNew and hasattr(self, '_dConnect'):
                d = defer.Deferred().addCallback(lambda _: self.connection)
                self._dConnect.chainDeferred(d)
            else:
                d = self._dConnect = \
                    self.q.call(self._engine.contextual_connect, doNext=True)
                d.addCallback(gotConnection)
            return d

        def gotConnection(connection):
            if hasattr(self, '_dConnect'):
                del self._dConnect
            self.connection = connection
            return connection

        # After all these function definitions, the method begins here
        if hasattr(self, '_engine'):
            return getConnection()
        else:
            return getEngine()

    def _sessionClose(self):
        """
        Replacement C{close} method for session objects.
        """
        self.isActive = False
        return self.session._close()

    def getSession(self):
        """
        Get a commitable session object
        """
        def gotConnection(connection):
            if SA04:
                d = self.q.call(
                    SA.orm.create_session, bind=connection, doNext=True)
            else:
                d = self.q.call(
                    SA.create_session, bind_to=connection, doNext=True)
            d.addCallback(gotSession)
            return d

        def gotSession(session):
            session.isActive = True
            session._close = session.close
            session.close = self._sessionClose
            self.session = session
            return session

        if hasattr(self, 'session') and self.session.isActive:
            return defer.succeed(self.session)
        return self.connect(forceNew=True).addCallback(gotConnection)
    
    def table(self, name, *cols, **kw):
        """
        Instantiates a new table object, creating it in the transaction thread
        as needed.

        One or more indexes other than the primary key can be defined
        via a keyword prefixed with I{index_} or I{unique_} and having
        the index name as the suffix. Use the I{unique_} prefix if the
        index is to be a unique one. The value of the keyword is a
        list or tuple containing the names of all columns in the
        index.
        """
        def _table():
            if not hasattr(self, '_meta'):
                if SA04:
                    self._meta = SA.MetaData(self._engine)
                else:
                    self._meta = SA.BoundMetaData(self._engine)
            indexes = {}
            for key in kw.keys():
                if key.startswith('index_'):
                    unique = False
                elif key.startswith('unique_'):
                    unique = True
                else:
                    continue
                indexes[key] = kw.pop(key), unique
            kw.setdefault('useexisting', True)
            table = SA.Table(name, self._meta, *cols, **kw)
            table.create(checkfirst=True)
            setattr(self, name, table)
            return table, indexes

        def _index(tableInfo):
            table, indexes = tableInfo
            for key, info in indexes.iteritems():
                kwIndex = {'unique':info[1]}
                try:
                    # This is stupid. Why can't I see if the index
                    # already exists and only create it if needed?
                    index = SA.Index(key, *[
                        getattr(table.c, x) for x in info[0]
                        ], **kwIndex)
                    index.create()
                except:
                    pass
        
        if hasattr(self, name):
            d = defer.succeed(False)
        else:
            d = self.connect()
            d.addCallback(lambda _: self.q.call(_table, doNext=True))
            d.addCallback(lambda x: self.q.call(_index, x, doNext=True))
        return d
    
    def startup(self):
        """
        This method runs before the first transaction to start my synchronous
        task queue. B{Override it} to get whatever pre-transaction stuff you
        have run.

        Alternatively, with legacy support for the old API, your
        pre-transaction code can reside in a L{userStartup} method of your
        subclass.
        """
        userStartup = getattr(self, 'userStartup', None)
        if callable(userStartup):
            return defer.maybeDeferred(userStartup)

    def userStartup(self):
        """
        If this method is defined and L{startup} is not overridden in your
        subclass, however, this method will be run as the first callback in the
        deferred processing chain, after my synchronous task queue is safely
        underway.

        The method should return either an immediate result or a deferred to
        an eventual result.

        B{Deprecated}: Instead of defining this method, your subclass should
        simply override L{startup} with your custom startup stuff.

        """

    def first(self):
        """
        This method automatically runs as the first transaction after
        completion of L{startup} (or L{userStartup}). B{Override it} to define
        table contents or whatever else you want as a first transaction that
        immediately follows your pre-transaction stuff.

        You don't need to decorate the method with C{@transact}, but it doesn't
        break anything if you do.
        """

    def shutdown(self, *null):
        """
        Shuts down my database transaction functionality and threaded task
        queue, returning a deferred that fires when all queued tasks are
        done and the shutdown is complete.
        """
        def finalTask():
            if hasattr(self, 'connection'):
                self.connection.close()
            self.running = False

        if self.running:
            d = self.q.call(finalTask)
            d.addBoth(lambda _: self.q.shutdown())
        else:
            d = defer.succeed(None)
        if hasattr(self, '_deferredTracker'):
            d.addCallback(lambda _: self._deferredTracker.deferToAll())
        return d
    
    def s(self, *args, **kw):
        """
        Polymorphic method for working with C{select} instances within a cached
        selection subcontext.

            - When called with a single argument (the select object's name as a
              string) and no keywords, this method indicates if the named
              select object already exists and sets its selection subcontext to
              I{name}.
            
            - With multiple arguments or any keywords, the method acts like a
              call to C{sqlalchemy.select(...).compile()}, except that nothing
              is returned. Instead, the resulting select object is stored in
              the current selection subcontext.
            
            - With no arguments or keywords, the method returns the select
              object for the current selection subcontext.
              
        """
        if kw or (len(args) > 1):
            # It's a compilation.
            context = getattr(self, 'context', None)
            self.selects[context] = SA.select(*args, **kw).compile()
        elif len(args) == 1:
            # It's a lookup to see if the select has been previously
            # seen and compiled; return True or False.
            self.context = args[0]
            return self.context in self.selects
        else:
            # It's a retrieval of a compiled selection object, keyed off
            # the most recently mentioned context.
            context = getattr(self, 'context', None)
            return self.selects.get(context)

    def queryToList(self, **kw):
        """
        Executes my current select object with the bind parameters supplied as
        keywords, returning a list containing the first element of each row in
        the result.
        """
        rows = self.s().execute(**kw).fetchall()
        if rows is None:
            return []
        return [row[0] for row in rows]

    def deferToQueue(self, func, *args, **kw):
        """
        Dispatches I{callable(*args, **kw)} as a task via the like-named method
        of my synchronous queue, returning a deferred to its eventual result.

        Scheduling of the task is impacted by the I{niceness} keyword that can
        be included in I{**kw}. As with UNIX niceness, the value should be an
        integer where 0 is normal scheduling, negative numbers are higher
        priority, and positive numbers are lower priority.
        
        @keyword niceness: Scheduling niceness, an integer between -20 and 20,
            with lower numbers having higher scheduling priority as in UNIX
            C{nice} and C{renice}.
        
        """
        return self.q.call(func, *args, **kw)


__all__ = ['transact', 'AccessBroker', 'SA']

