#! /usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Consola con el modelo.
Aca deberíamos implementar los comandos de desarrollo.
* sql_drop
* sql_dump
etc.
'''
import sys
import re
from optparse import OptionParser

# Configuracion
from config import Config

# Parseo de argumentos
from optparse import OptionParser

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import OperationalError
  
# Modelo de la base de datos
from model import *



def build_db_url(type=None, dbname=None, user=None, password=None, host=None, 
                 port=None, options=None, **kargs):
    '''
    Construye la URL con formato RFC-1738 para SQLAlchemy
  verbosity : 1
  type : 'mysql'
  user : 'dsem'
  password : 'passmenot'
  host : 'localhost'
  port : 3306
  dbname : 'dsem'
  options : ''
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
    if options:
        tmp = '%s&%s' % (tmp, '&'.join(map( lambda x, y: '%s=%s' % (x, y), options.items() )))
    return tmp


def shell_base(options):
    #TODO: Implementar
    print "Shell"
    
    
    #print options.config.scada
    url = build_db_url(**options.config.scada)
    engine = create_engine(url, echo=(options.verbose))
    try:
        connection = engine.connect()
    except OperationalError, e:
        print "Error en la conexion con %s %s" % (options.db_engine, e)
        sys.exit()
    
    metadata.bind = engine
    
    try:
        metadata.create_all(engine)
    except NotImplementedError:
        # Por alugna razon no funciona del todo bien esto
        pass
    Session = sessionmaker(bind=engine)
    session = Session() #@UnusedVariable

    
    from IPython.Shell import IPShellEmbed #@UnresolvedImport
    ipshell = IPShellEmbed()
    
    print "*** Definicion del modelo ***"
    print "Variables de SQLAlchemy: session, engine y metadata"
    print "Creando tablas de ser necesario...",
    try:
        metadata.create_all(connection)
    except NotImplementedError, e:
        print "No implementado %s. OK" % e
    else:
        print "OK"
    print "Consulte la documentacion de SQLAlchemy en http://www.sqlalchemy.org/docs/05/intro.html"
    
    def create_con(ip_address, uc_ids):
        ''' Ayuda para crear concentrador con UCs '''
        co = CO(ip_address)
        session.add(co)
        
        
        for id in uc_ids:
            print co.id_CO
            session.add(UC(co.id_CO, id))
        session.commit()
    
    def clean():
        print "Limpiando base"
        map(session.delete, session.query(DI).all())
        map(session.delete, session.query(AI).all())
        map(session.delete, session.query(SV).all())
        map(session.delete, session.query(EV).all())
        print "OK"
        
    def recreate(name = None):
        ''' Recreate a table '''
        if name:
            print "Recreating %s" % name
            table = metadata.tables[name]
            table.drop()
            table.create()
        else:
            for name, table in metadata.tables.iteritems():
                print "Recreating %s... " % name,
                table.drop()
                table.create()
                print "OK"
        
    # Lanzamos una consola
    ipshell() # this call anywhere in your program will start IPython

def callesimport():
    RE_COMP = re.compile('\.*>(.*)</text>', re.MULTILINE | re.UNICODE)
    data = sys.stdin.read()
    match = RE_COMP.search(data)
    print match.groups()

def cargar_configuracion(option, opt_str, value, parser):
    '''
    Cargar la configuracion a mediante el modulo config.
    '''
    from optparse import OptionValueError
    from config import ConfigFormatError
    try:
        config = Config(value)
    except IOError:
        raise OptionValueError('No se encuentra %s' % value)
    except ConfigFormatError, e:
        raise OptionValueError('Archivo de configuracion %s mal formateado «%s»' % (value, e))
    print "La config es:", config
    setattr(parser.values, 'config', config)

def main(argv = sys.argv):
    #usage, option_list, option_class, version, conflict_handler, description, formatter, add_help_option, prog, epilog
    parser = OptionParser(usage = "%s [OPTIONS] COMANDO [ COMANDO ... ]" % argv[0] )
    parser.add_option('-c', '--config', action='callback', type=str, callback = cargar_configuracion, nargs = 1,
                      help = ''' Especifica el archivo CFG de configuracion ''')
    parser.add_option('-v', '--verbose', action="store_true", dest='verbose', default = False, 
                      help = ''' Salida de depuracion ''')
    opts, args = parser.parse_args(argv)
    #if not opts.
    for cmd in args[1:]:
        if cmd == 'shell':
            print "Inciando shell con la DB..."
            shell_base(opts)
            
        elif cmd == 'callesimport':
            callesimport()
        else:
            print "No se reconoce el comando %s" % cmd
            sys.exit(-3)
    else:
        print "No se especificaron opciones"
     
if __name__ == '__main__':
    sys.path += ('..', '../..')
    sys.exit(main())
        
    
