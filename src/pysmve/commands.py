# Comandos para el main


import functools
from operator import itemgetter
import exceptions
from logging import getLogger
from protocols.mara import MaraServerFactory
logger = getLogger(__name__)


COMMANDS = {}

def command(obj):
    global COMMANDS
    if not callable(obj):
        raise exceptions.ImproperlyConfigured("Task should be callable objects")
    
    
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
def server(options, reload=False):
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
        
        reactor.listenTCP(options.port, site)
        reactor.callLater(1, functools.partial(open_local_browser, port=options.port))    
        print "Iniciando servidor en http://0.0.0.0:%s" % options.port
        reactor.run()

def getprofile(name, fail=True):
    from peewee import DoesNotExist
    from models import Perfil
    try:
        return Perfil.get(nombre=name)
    except DoesNotExist:
        if fail:
            print "No existe el perfil %s" % name
            raise
            #sys.exit(-1)
        return None
    

@command
def maraserver(options):
    """Run server protocol"""
    from models import database, Perfil
    from twisted.internet import reactor
    try:
        database.connect()
        profile = getprofile(options.profile)
        for comaster in profile.comaster_set:
            print "Conectando con ", comaster
            reactor.listenTCP(comaster.direccion, comaster.port, MaraServerFactory(comaster))
        print "Run..."
        reactor.run()
    except Exception:
        from traceback import format_exc
        print format_exc()
        raise
@command
def maraclient(options):
    from models import database, Perfil
    database.connect()
    profile = getprofile(options.profile)
    
    
@command
def cloneprofile(options, dest):
    print "Copying profile %s to %s" % (options.profile, dest)
    

@command
def server_plus(options, restart=False, kill=False):
    while True:
        try:
            server(options, restart)
        except Exception as e:
            print e, type(e)
            import sys; sys.exit()
    
@command
def dbshell(options):
    from models import Perfil, COMaster, IED, VarSys, DI, Evento, AI, Energia
    print "Importing: Perfil, COMaster, IED, VarSys, DI, Evento, AI, Energia"
    
    from IPython import embed
    embed()
    
@command
def syncdb(options, reset=False, create=False):
    from models import DB_FILE, database, crear_tablas, cargar_tablas
    import os
    if reset:
        os.unlink(DB_FILE)
        database.connect()
        crear_tablas()
        cargar_tablas()
    elif create:
        database.connect()
        crear_tablas()

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