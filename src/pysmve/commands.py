# Comandos para el main


import functools
import exceptions

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
def server(options, restart=False):
    from app import app
    print "Running server"
    if options.reload:
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
        reactor.callLater(1, partial(open_local_browser, port=options.port))    
        print "Iniciando servidor en http://0.0.0.0:%s" % options.port
        reactor.run()
    
@command
def server_plus(options):
    print "Server plus"
    
@command
def dbshell(options):
    pass
    
@command
def syncdb(options, recreate=False):
    pass
    


if __name__ == '__main__':
    # Print available commands
    print COMMANDS.keys()

    
    
