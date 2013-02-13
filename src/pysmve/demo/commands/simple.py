# encoding: utf-8
# Comandos para el main

import functools
from operator import itemgetter
from errors import ImproperlyConfigured
from logging import getLogger
from prettytable import PrettyTable
logger = getLogger(__name__)

# Implemnetanción sencilla de comandos al estilo Django.
# Un único punto de entrada para
#===============================================================================
# Path Fix
#===============================================================================
import sys, os
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_PATH, '..'))

from protocols.mara import MaraServerFactory, MaraClientProtocolFactory


COMMANDS = {}

def command(obj):
    global COMMANDS
    if not callable(obj):
        raise ImproperlyConfigured("Task should be callable objects")


    @functools.wraps(obj)
    def wrapped(*largs, **kwargs):
        # ------------------------------------------------------------
        # Run command in context
        # ------------------------------------------------------------
        return obj(*largs, **kwargs)
    COMMANDS[obj.func_name] = obj
    return wrapped

def open_local_browser(port):
    print "Lanzando browser"
    import webbrowser
    webbrowser.open('http://localhost:%d/' % port)


@command
def webserver(options, reload=False):
    from app import app
    print "Running server"
    if reload:
        # Con flask
        print "Trabajando con flask stand-alone"
        import gevent.wsgi
        from gevent import monkey
        import werkzeug.serving
        werkzeug.serving
        # http://flask.pocoo.org/snippets/34/ (2nd comment)
        monkey.patch_all()

        @werkzeug.serving.run_with_reloader
        def runServer():
            app.debug = True
            ws = gevent.wsgi.WSGIServer(('', options.port), app)
            ws.serve_forever()

        app.run()

    else:
        # Con Twisted
        from resources import site
        from twisted.internet import reactor

        from models import COMaster
        for x in COMaster.select():
            print x

        reactor.listenTCP(options.port, site) #@UndefinedVariable
        reactor.callLater(1, functools.partial(open_local_browser, port=options.port))    #@UndefinedVariable
        print "Iniciando servidor en http://0.0.0.0:%s" % options.port
        reactor.run() #@UndefinedVariable

@command
def maraserver(options):
    """Run server protocol"""
    from models import database, Profile
    from twisted.internet import reactor
    try:
        database.connect()
        profile = Profile.get(name=options.profile)
        #import IPython; IPython.embed()
        for comaster in profile.comaster_set.filter(enabled=True):
            print "Listening in port %d" % comaster.port
            reactor.listenTCP(comaster.port, MaraServerFactory(comaster)) #@UndefinedVariable
        reactor.run() #@UndefinedVariable
    except Exception:
        from traceback import format_exc
        print format_exc()
        raise

@command
def maraclient(options):
    '''
    Conexión con el mara
    '''
    from twisted.internet import reactor
    try:
        from models import database, Profile
        database.connect()
        profile = Profile.get(name=options.profile)

        for comaster in profile.comaster_set.filter(enabled=True):
            print "Conectando con %s" % comaster
            reactor.connectTCP(comaster.address,
                               comaster.port,
                               MaraClientProtocolFactory(comaster),
                               timeout=comaster.timeout,
                               #bindAddress=None,
                               )
        # Una vez que está conectado todo, debemos funcionar...
        reactor.run() #@UndefinedVariable
    except Exception as e:
        from traceback import format_exc
        print format_exc()
        print e

@command
def cloneprofile(options, dest):
    print "Copying profile %s to %s" % (options.profile, dest)
    print "Not implemented yet"

@command
def dbshell(options):
    from models import Profile, COMaster, IED, VarSys, DI, Event, AI, Energy
    print "Importing: Perfil, COMaster, IED, VarSys, DI, Evento, AI, Energia"

    from IPython import embed
    embed()

@command
def syncdb(options, reset=False, create=False):
    from models import DB_FILE, database, create_tables, populate_tables
    import os
    if reset:
        os.unlink(DB_FILE)
        database.connect()
        create_tables()()
        populate_tables()
    elif create:
        database.connect()
        create_tables()()

    else:
        dbshell(options)


@command
def help(options, **kwargs):
    from inspect import getargspec
    if kwargs:
        for command_name in kwargs.keys():
            func = COMMANDS.get(command_name, None)
            if func is None:
                print "%s does not exist!"
                return -1
            # Function names
            print

    print "Available commands:\n"
    for name, command in sorted(COMMANDS.items(), key=itemgetter(0)):
        print "    *", name
        arguments = getargspec(command).args[1:]
        if arguments:
            print "        %s" % ", ".join(arguments)


@command
def emulator(options, listen=None):
    listen_port = 9736 if listen == None else int(listen)
    print "Running emulator on port %s" % listen_port
    raise NotImplementedError("Esto falta implementarlo")

@command
def rebuilddb(options):
    '''
    Rebuild DB
    '''
    from peewee import drop_model_tables, create_model_tables, find_subclasses
    from models import BaseModel, populate_tables
    print "Reconsruyendo la base de datos..."
    models = find_subclasses(BaseModel)
    print "Drop tables..."
    drop_model_tables(models)
    print "Cereate tables..."
    create_model_tables(models)
    CONFIG = {
            'default':[
                    dict(address='192.168.1.97', description="Placa de prueba 1 "),
                    dict(address='192.168.1.98', description="Placa de prueba 2"),
            ],
            'test':[
                dict(address='127.0.0.1', description=u"Conexión con localhost"),
            ]
        }
    print "Populating..."
    for name, list_of_comaster_cfg in CONFIG.iteritems():
        populate_tables(name, list_of_comaster_cfg)

@command
def shell(options):
    '''
    Interactive shell with database access
    '''
    from peewee import find_subclasses
    from models import (
                        Profile,
                        COMaster,
                        IED,
                        VarSys,
                        DI,
                        AI,
                        MV,
                        Event,
                        Energy,
                        BaseModel, )
    #for comaster in Profile.by_name(options.profile).comaster_set():
    #    src = 'co%s = comaster' % comaster.addres[-3:]
    #    exec(src)
    from datetime import datetime, date
    from IPython import embed
    models = find_subclasses(BaseModel)
    for model in models:
        print "Importing model %s" % model.__name__
    embed()

@command
def enableone(options, comaster='192.168.1.98', profile='default'):
    '''Hablita un comaster en particular %s''' % comaster
    from models import Profile
    comasters = Profile.get(name=profile).comaster_set
    comasters.exclude(address=comaster).update(enabled=False)
    co = comasters.get(address=comaster)
    co.enabled = True
    co.save()

@command
def listenabled(options, profile='default', all=False):
    '''Lista las comasters'''
    from models import Profile, COMaster
    if not all:
        cos = Profile.get(name=profile).comaster_set
    else:
        cos = COMaster.select()

    for co in Profile.get(name=profile).comaster_set:
        print co.address, co.enabled


@command
def profilelist(options):
    from models import Profile
    x = PrettyTable(["Name", "Version", "Date", "IEDs"])
    for profile in Profile.select():
        row = (
               profile.name,
               profile.version,
               profile.date.strftime("%d/%m/%Y %X"),
               " - ".join(map(unicode, profile.comaster_set))
               )
        x.add_row(row)

    print x



