# encoding: utf-8
# Comandos para el main


import functools
from operator import itemgetter
from errors import ImproperlyConfigured 
from logging import getLogger
from protocols.mara import MaraServerFactory, MaraClientProtocolFactory
logger = getLogger(__name__)


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
            reactor.listenTCP(comaster.port, MaraServerFactory(comaster)) #@UndefinedVariable
        reactor.run()
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
        
        for comaster in profile.comaster_set:
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