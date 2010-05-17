#! /usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Unificación de acceso a la DB de Qt mediante una URL y
query's con __getattribute__
'''

# Exported symbols
__all__ = ('dburl_to_qsqldb', 'PyQSqlQuery', )

from PyQt4.QtSql import *
from PyQt4.QtCore import QVariant
import re

QT_SQL_TYPES = {
    'mysql': 'QMYSQL',
    'sqlite': 'QSQLITE',
    'postgres': 'QPSQL',
}



REG_DB = '''
(?P<type>\w{2,15})://    # Tipo de la base de datos
(?:
   (?:
       (?P<user>[\w\d]{1,50})
       (?::(?P<pass>[\w\d]{1,50}))?
       @
   )?
   (?P<host>[\w]*)
   (?::(?P<port>[\d]{3,5}))?
)?\/   # Puso user:pass@host
(?P<db>[\w]+) # Nombre de la base, siempre es obligatorio
(?:\?(?P<params>[\w]*(?:\=[\w\d]+)))? # Parametros extra de la 
'''

REG_DB = re.compile(REG_DB, re.VERBOSE | re.UNICODE)

class DBDecodeException(Exception):
    '''
    Excepcion en la DB
    '''
    def __init__(self, why, *largs):
        if type(why) == QSqlError:
            why = "%s-%s" % ( why.databaseText(), why.driverText() )
        else:
            Exception.__init__(self, why, *largs)


def dburl_to_qsqldb(db_str = None, **kwargs):
    '''
    DB URL -> QSqlDatabase instance (connection)
    '''
    if not db_str and kwargs:
        db_str = build_db_url(**kwargs)
    match = REG_DB.match(db_str)
    if not match:
        raise DBDecodeException("No match for %s" % db_str)
    groupdict = match.groupdict()
    qdb = QSqlDatabase.addDatabase(QT_SQL_TYPES[groupdict['type']])
    
    qdb.setHostName(groupdict["host"])
    try:
        qdb.setPort(int(groupdict["port"]))
    except KeyError, ValueError:
        pass
    
    try:
        qdb.setUserName(groupdict["user"])
    except KeyError:
        pass
    try:
        qdb.setPassword(groupdict["pass"])
    except KeyError:
        pass
    
    qdb.setDatabaseName(groupdict["db"])
    if not qdb.open():
        raise DBDecodeException( qdb.lastError().databaseText() )
        #raise DBDecodeException(qdb.lastError())
    return qdb

# Tomada de un modulo que usaba la aplicacion CLI
def build_db_url(type=None, dbname=None, user=None, password=None, host=None, 
                 port=None, args=None, **kwargs):
    '''
    Construye la URL con formato RFC-1738 para SQLAlchemy.
    
        type://user:pass@host:port/dbname?args
        
    El kwargs se usa para que no le afecen los parametros de mas
    '''
    tmp = '%s://' % type
    if user and host:
        if password:
            tmp = '%s%s:%s@' % (tmp, user, password)
        else:
            tmp = '%s%s@' % (tmp, user)
    if host:
        if port:
            tmp = '%s%s:%d' % (tmp, host, port)
        else:
            tmp = '%s%s' % (tmp, host)
    tmp = '%s/%s' % (tmp, dbname)
    #TODO: Pasaje de parametros ?xxx=yyy&zzz=jjj
    return tmp

class PyQSqlQuery(QSqlQuery):
    '''
    Una consulta que define como de la isntancia, los miembros de la tupla en
    la DB.
    
    '''
    class PyQSqlQueryIterator(object):
        ''' Iterador sobre un queryset '''
        def __init__(self, qs):
            self.qs = qs
            
        def next(self):
            self.qs.next()
            if self.qs.isValid():
                return self.qs
            else:
                raise StopIteration()
        
        
    def __getattr__(self, name):
        if not self.isValid():
            self.next()
        
        pos = self.record().indexOf(name)
        if pos >= 0:
            variant = self.value( pos )
            v_type = variant.type()
            if v_type == QVariant.Invalid:
                return None
            elif v_type == QVariant.Int:
                val, ok = variant.toInt()
                if ok:
                    return val
                else:
                    raise ValueError('Error con %s', variant)
            elif v_type == QVariant.Double:
                val, ok = variant.toDouble()
                if ok:
                    return val
                else:
                    raise ValueError('Error con %s', variant)
            elif v_type == QVariant.LongLong:
                val, ok = variant.toLongLong()
                if ok:
                    return val
            elif v_type == QVariant.String:
                return unicode(variant.toString())
            elif v_type == QVariant.DateTime:
                return variant.toDateTime()
            
            else:
                raise ValueError("No se convertir el tipo %d de QVariant" % v_type)
            
        return QSqlQuery.__getattribute__(self, name)
    
    def __iter__(self):
        ''' Iterador '''
        return PyQSqlQuery.PyQSqlQueryIterator(self)
    
    
    
if __name__ == '__main__':
    import sys
    sys.path += ('..', '../..')
    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)
    conn = dburl_to_qsqldb('mysql://dsem:passmenot@localhost:3306/dsem')
    app.db_con = conn
    
    
    query = PyQSqlQuery('SELECT * FROM Calle GROUP BY Calle.nombre')
    for esquina in query:
        print esquina.nombre
    