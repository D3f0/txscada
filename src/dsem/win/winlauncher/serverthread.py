#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from Queue import Queue
from PyQt4 import QtCore
from PyQt4.QtGui import QApplication
from cherry_server import run_django_under_cherrypy
from cherrypy import server, engine

class ServerThread(QtCore.QThread):
    '''
    La arquitectura de cherrypy nos permite no utilizar bloqueos
    '''
    def __init__(self, *largs):
        QtCore.QThread.__init__(self, *largs)
        self.queue = Queue()
        self.app = QApplication.instance()
        #self.start()
        
    def server_start(self):
        self.start()
        if self.app.start_browser:
            print "Abrir browser"
        
    def server_stop(self):
        # Esto debería desbloquear el hilo
        server.stop()
        #engine.stop()
        self.terminate()
        self.emit(QtCore.SIGNAL("stoped()"), None)
        
    def server_restart(self):
        server.stop()
        self.server_start()
        
    
    def run(self):
        
        run_django_under_cherrypy('dscada', self.app.port, None, self.app.start_browser)
#        while True:
#            task = self.queue.get()
#            self.emit(QtCore.SIGNAL("started()"), None)
#            # Arrancar el servidor
#            var = run_django_under_cherrypy('dscada', None, True)
#            if not val:
#                self.emit(QtCore.SIGNAL("aborted"), "Puerto en uso")
#            
