#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import wsgiserver
#This can be from cherrypy import wsgiserver if you're not running it standalone.
import sys,os
sys.path.append(os.path.abspath('..'+os.sep+'..'))

import django.core.handlers.wsgi
import webbrowser
from django.core.servers.basehttp import AdminMediaHandler
 
def run_server():
    sys.path.append('..')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'dscada.settings'
    
    from dscada import settings
    print settings
    
    app = AdminMediaHandler(django.core.handlers.wsgi.WSGIHandler())
    #logged_app = TransLogger(app)
    server = wsgiserver.CherryPyWSGIServer(    
        ('127.0.0.1', 8080),
        app,
        server_name='luz.lifeway.org',
        numthreads = 20,
    )
 
    try:
        server.start()
        webbrowser.open('http://127.0.0.1:8080')
    except KeyboardInterrupt:
        server.stop()
if __name__ == "__main__":
    run_server()