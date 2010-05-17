"""

Introduction
============

B{sAsync} is an enhancement to the SQLAlchemy package that provides persistent
dictionaries, text indexing and searching, and an access broker for
conveniently managing database access, table setup, and
transactions. Everything can be run in an asynchronous fashion using the
Twisted framework and its deferred processing capabilities.

Copyright (C) 2006-2007 by Edwin A. Suominen, U{http://www.eepatents.com}


Licensing
=========

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License (GPL) as published by the Free
Software Foundation; either version 2 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.

You should have received a copy of the GPL along with this program; if not,
write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.


Usage
=====

sAsync wraps your SQLAlchemy database access code inside asynchronous
transactions.  At the lowest level, it provides a @transact decorator for
your database-access methods that makes them immediately return a Twisted
Deferred object.

For example, suppose you want to run a method that selects a list of row
objects from a table. Instead of waiting around for your method to return the
list, blocking everything else your program is trying to do, you decorate it
with @transact and run it. It immediately hands you a Deferred, and
you scribble the name of your callback function on it, handing the Deferred
back to your decorated method. (You can also keep a copy of it (i.e., a
reference to the object) around if you like, for example to add other
callbacks.)

Once you've attached your callback function to the Deferred result, you can
go on with your business, knowing that SQLAlchemy will be cranking away behind
the scenes (in a transaction-specific thread) to obtain a result for you.  When
the result is finally ready, your transact-decorated method will look at the
Deferred, see the note you scribbled on it (Pls call this function with
the result. Thx!), and give your function a call with the list of rows. It
will supply the callback with the list as the function's argument.

You can also do some asynchronous database operations on a higher level. For
example, you can maintain a store of Python objects, with each object
accessible (with deferred results) via a unique key. If that sounds like what a
dictionary does, it should! The ''sAsync'' package also provides a
dictionary-like object with database-persistent items that you can access in an
asynchronous fashion.

And, someday, someone will get the full-text searching capabilities working. Of
course, the results of your potentially time-consuming searches will be done in
the same asynchronous fashion.

"""

def engine(url, **kw):
    """
    Specifies the parameters for creating an SQLAlchemy database engine that
    will be used as a default for all instances of L{AccessBroker} and all
    persistent objects based thereon.

    @param url: An RFC-1738 url to a database connection.
          
    @keyword strategy: The Strategy describes the general configuration used to
        create this Engine. The two available values are plain, which is the
        default, and threadlocal, which applies a 'thread-local context' to
        implicit executions performed by the Engine. This context is further
        described in Implicit Connection Contexts.

    @type strategy: 'plain'.

    @keyword pool: An instance of sqlalchemy.pool.Pool to be used as the
        underlying source for connections, overriding the engine's connect
        arguments (pooling is described in Connection Pooling). If C{None}, a
        default Pool (usually QueuePool, or SingletonThreadPool in the case of
        SQLite) will be created using the engine's connect arguments.

    @type pool: C{None}

    @keyword pool_size: The number of connections to keep open inside the
        connection pool. This is only used with QueuePool.

    @type pool_size: 5

    @keyword max_overflow: The number of connections to allow in 'overflow,'
        that is connections that can be opened above and beyond the initial
        five. This is only used with QueuePool.

    @type max_overflow: 10
    
    @keyword pool_timeout: number of seconds to wait before giving up on
        getting a connection from the pool. This is only used with QueuePool.

    @type pool_timeout: 30

    @keyword echo: if C{True}, the Engine will log all statements as well as a
        repr() of their parameter lists to the engines logger, which defaults
        to sys.stdout. The echo attribute of ComposedSQLEngine can be modified
        at any time to turn logging on and off. If set to the string 'debug',
        result rows will be printed to the standard output as well.

    @type echo: C{False}

    @keyword logger: a file-like object where logging output can be sent, if
        echo is set to C{True}. Newlines will not be sent with log messages. This
        defaults to an internal logging object which references sys.stdout.

    @type logger: C{None}

    @keyword module: used by database implementations which support multiple
        DBAPI modules, this is a reference to a DBAPI2 module to be used
        instead of the engine's default module. For Postgres, the default is
        psycopg2, or psycopg1 if 2 cannot be found. For Oracle, its cx_Oracle.

    @type module: C{None}

    @keyword use_ansi: used only by Oracle; when C{False}, the Oracle driver
        attempts to support a particular 'quirk' of Oracle versions 8 and
        previous, that the LEFT OUTER JOIN SQL syntax is not supported, and the
        'Oracle join' syntax of using <column1>(+)=<column2> must be used in
        order to achieve a LEFT OUTER JOIN.

    @type use_ansi: C{True}

    @keyword threaded: used by cx_Oracle; sets the threaded parameter of the
        connection indicating thread-safe usage. cx_Oracle docs indicate
        setting this flag to C{False} will speed performance by 10-15%. While this
        defaults to C{False} in cx_Oracle, SQLAlchemy defaults it to C{True},
        preferring stability over early optimization.

    @type threaded: C{True}

    @keyword use_oids: used only by Postgres, will enable the column name 'oid'
        as the object ID column, which is also used for the default sort order
        of tables. Postgres as of 8.1 has object IDs disabled by default.

    @type use_oids: C{False}

    @keyword convert_unicode: if set to C{True}, all String/character based types
        will convert Unicode values to raw byte values going into the database,
        and all raw byte values to Python Unicode coming out in result
        sets. This is an engine-wide method to provide unicode across the
        board. For unicode conversion on a column-by-column level, use the
        Unicode column type instead.

    @type convert_unicode: C{False}

    @keyword encoding: the encoding to use for all Unicode translations, both
        by engine-wide unicode conversion as well as the Unicode type object.

    @type encoding: 'utf-8'

    """
    from database import AccessBroker
    AccessBroker.globalParams = url, kw
    
