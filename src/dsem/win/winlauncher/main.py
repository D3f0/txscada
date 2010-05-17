#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import os, sys
sys.path.extend ( ('..', '..%s..' % os.sep) )
from PyQt4 import QtCore, QtGui
from winlauncher.tray import UcnetTrayIcon
from glob import glob
from atexit import register
import signal

def cleanup(file):
    try:
        os.unlink(file)
    except:
        pass
    try:
        import cherrypy
        cherrypy.server.stop()
    except:
        pass

def create_lock(pid = os.getpid()):
    lock_name = "%s.lck" % pid
    file = open(lock_name, "w+")
    file.flush()
    return lock_name

def clean_locks(locks):
    for name in locks or glob("*.lck"):
        try:
            pid = int(name[:4])
            print "Terminando: ",pid
            os.kill(pid, signal.SIGKILL)
        except Exception, e:
            print e
            pass
        os.unlink(name)
#------------------------------------------------------------------------------ 
class UcnetLauncherApp(QtGui.QApplication):
    ''' Aplicación '''
    DO_NOT_ASK = 1
    
    def __init__(self, *largs):
        QtGui.QApplication.__init__(self, *largs)
        self.__app_name = None
        # Configuración de la aplicación
        self.__config = None
        
    @property    
    def config(self):
        ''' Getter para la configuración (singletón y de solo lectura) '''
        if not self.__config:
            self.__config = QtCore.QSettings("PicNet Crew", "SemCtl")
        return self.__config
     
    def exec_(self):
        locks = glob('*.lck')
        if not locks:
            register(cleanup, create_lock())
        else:
            resp = \
            QtGui.QMessageBox.warning(None,
                                       self.trUtf8("Error"),
                                       self.trUtf8("Ya existe una instancia en ejecución de %s<br />" % self.app_name()+
                                                   "Si no es el caso, por favor borre <b>*.lck</b> de"+
                                                   "%s" % os.getcwd()),
                                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                        QtGui.QMessageBox.No)
            if resp == QtGui.QMessageBox.No:
                return self.exit(UcnetLauncherApp.DO_NOT_ASK)
            else:
                clean_locks(locks)
                register(cleanup, create_lock())
            
        # Como no tenemos una ventana principal...
        self.setQuitOnLastWindowClosed(False)
        self.tray = UcnetTrayIcon()
        self.tray.show()
        return QtGui.QApplication.exec_()
    
    def exit(self, val = None):
        ''' Pregunta si está seguro de desar salir '''
        if val == UcnetLauncherApp.DO_NOT_ASK:
            self.quit()
        # TODO: Recordar la respuesta
        resp = \
        QtGui.QMessageBox.question(None,
                                   self.trUtf8("Está seguro de que desea salir?"),
                                   self.trUtf8("Está seguro de que desea <i>salir</i> de %s" % self.app_name()),
                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                   QtGui.QMessageBox.No)
        if resp == QtGui.QMessageBox.Yes:
            return QtGui.QApplication.exit(resp)
            
    def app_name(self):
        ''' Nombre de la aplicación '''
        if not self.__app_name:
            self.__app_name = "<b>µC Net</b> (rev.%s)" % (os.popen('hg id -n').read().strip() or "?")
        return self.__app_name
    
#================================================================================
# Prpperties
#================================================================================
    # Port
    def _get_port(self):
        port, ok = self.config.value('server/port').toInt()
        return ok and port or 8080
    def _set_port(self, val):
        self.config.setValue('server/port', QtCore.QVariant(val))
    port = property(_get_port, _set_port)
    
    # Start browser on server start
    def _get_start_browser(self):
        return self.config.value('options/start_browser').toBool()
    
    def _set_start_browser(self, val):
        self.config.setValue('options/start_browser', QtCore.QVariant(val))
    start_browser = property(_get_start_browser, _set_start_browser)
                    
def main(argv = sys.argv):
    ''' Punto de entrada al programa '''
    app = UcnetLauncherApp(argv)
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
