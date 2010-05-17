#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from gui.mainwin import MainWin
import sys
import os

class PySemControlApplication(QtGui.QApplication):
    '''
    Aplicacion de scada
    '''
    def __init__(self, args = []):
        QtGui.QApplication.__init__(self, args)
        if not self.check_one_instance():
            QtGui.QMessageBox.information(None, "Error", 
                u"Ya se encuentra una aplicacion en ejecución")
            return QtGui.qApp.exec_()
        
        # No cerrar cuando la ultima ventana se cierra
        self.setQuitOnLastWindowClosed(False)
        self.main_win =  MainWin()
        
        self.tray_icon = QtGui.QSystemTrayIcon()
        self.tray_icon.setIcon(QtGui.QIcon(':/icons/res/view-statistics.png'))
        
        # Menú para el ícono de la barra tray
        self.tray_menu = QtGui.QMenu()
        self.action_salir = self.tray_menu.addAction('Salir')
        self.action_salir.setIcon(QtGui.QIcon(':/icons/res/application-exit.png'))
        self.action_ventana = QtGui.QAction('Mostrar ventana principal', self.tray_menu)
        # Conexion de la ventana
        self.connect(self.action_ventana, QtCore.SIGNAL('toggled(bool)'), self.toggleVentana)
        
        self.connect(self.main_win, QtCore.SIGNAL('hidden()'), self.hideMainWin)
        
        self.action_ventana.setCheckable(True)
        
        self.tray_menu.addAction(self.action_ventana)
        
        self.connect(self.action_salir, QtCore.SIGNAL("triggered()"), QtGui.qApp.exit)
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Mostrar la vetnana principal
        #self.main_win.show()
        
        
        # Primero mostramos el icono en la barra tray
        self.tray_icon.show()
        # Luego mostramos la vetana
        self.action_ventana.setChecked(True)
        
        
    def hideMainWin(self):
        self.action_ventana.setChecked(False)
        
    def toggleVentana(self, checked):
        if checked:
            self.main_win.show()
        else:
            self.main_win.hide()
        
    def path(self):
        '''
        Detección de ruta, acá nos tenemos que fijar si estamos
        corriendo desde el script o desde el ejecutable.
        '''
        if not hasattr(self, '_path'):
            if sys.platform.count('linux'):
                self._path = os.path.dirname(__file__)
            
            elif sys.platform.count('win'):
                if hasattr(sys, "frozen") and sys.frozen == 1:
                    # Si creamos un ejecutable con PyInstaller
                    self._path = os.path.dirname(sys.executable)
                else:
                    print "Averigurar el path en windows"
                    self._path = None
        
        return self._path
    
    def res_path(self, path):
        ''' Devuelve la ubicación de un recurso '''
        pass
        
    def exec_(self):
        '''
        Todavía nada...
        '''
        print "Corriendo la aplicacion"
        return QtGui.qApp.exec_()
    
    def check_one_instance(self):
        '''
        Bifurcamos el checkeo de una instancia según la plataforma.
        '''
        if sys.platform.count('win'):
            return self._check_one_instance_win()
        else:
            return self._check_one_instance_unix()
        
    def _check_one_instance_win(self):
        '''
        Esta es la implementación para win de solo una instancia
        activa. En el caso de que existan dos instancias de la 
        aplicación, este método devuelve True.
        '''
        from win32event import CreateMutex
        from win32api import GetLastError
        from winerror import ERROR_ALREADY_EXISTS
        self.connect(self, QtCore.SIGNAL("aboutToQuit()"), self._win_mutex_destroy)
        
        self.mutexname = "testmutex_{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
        self.mutex = CreateMutex(None, False, self.mutexname)
        self.lasterror = GetLastError()
        return (self.lasterror != ERROR_ALREADY_EXISTS)
    
    

    def _win_mutex_destroy(self):
        '''
        Esto es necesario para quitar el Mutex en win32
        '''
        from win32api import CloseHandle
        CloseHandle(self.mutex)

    
    def _check_one_instance_unix(self):
        '''
        Checkeo de uns instancia UNIX.
        '''
        # FIXME: No funciona
        import fcntl
        pid_file = 'program.pid'
        fp = open(pid_file, 'w')
        try:
            fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            return False
    
if __name__ == "__main__":
    ''' Arrancar la aplicación '''
    import sys
    app = PySemControlApplication(sys.argv)
    sys.exit(app.exec_())