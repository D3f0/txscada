#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath('..'))
import cherrypy
import webbrowser

from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.basehttp import AdminMediaHandler
os.environ[ 'DJANGO_SETTINGS_MODULE' ] = "dscada.settings"
from django.conf import settings

def run_django_under_cherrypy(project, port, static_media, open_brwoser = False, chpy_env = None):
    
    print "Iniciando"
    if not chpy_env:
        chpy_env = 'staging'
        
    if not static_media:
        static_media = settings.ADMIN_MEDIA_ROOT
            
    cherrypy.config.update({
        'environment': 'staging',
        'log.error_file': 'site.log',
        'log.screen': True,
    })
    cherrypy.tree.graft(
        AdminMediaHandler(
                          WSGIHandler(),
                          media_dir = static_media
                          ), '/')
    
    cherrypy.server.socket_port = port
    
    try:
        try:
            cherrypy.server.quickstart()
        except DeprecationWarning,e:
            pass
        cherrypy.engine.start()
    except IOError, e:
        # El puerto puede estar ocupado
        return False
    

if __name__ == "__main__":

    try:
        pth = __import__('django', {},{}, ['*']).__path__[0]
        full_media_path = os.path.join(pth, 'contrib', 'admin', 'media')
        run_django_under_cherrypy('dscada', full_media_path, True)
    except KeyboardInterrupt:
        cherrypy.server.stop()
