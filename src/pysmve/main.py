#!/usr/bin/env python2
# encoding: utf-8

import sys
from functools import partial

def check():
    import os
    assert 'VIRTUAL_ENV' in os.environ, "Falta el virtualenv"

def open_local_browser(port):
    print "Lanzando browser"
    import webbrowser
    webbrowser.open('http://localhost:%d/' % port)
        

def main(argv = sys.argv):
    # Aplicación
    
    from app import app
    from options import parser

    options = parser.parse_args()
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
        
        reactor.listenTCP(options.port, site)
        reactor.callLater(1, partial(open_local_browser, port=options.port))    
        print "Iniciando servidor en http://0.0.0.0:%s" % options.port
        reactor.run()

if __name__ == "__main__":
    sys.exit(main())