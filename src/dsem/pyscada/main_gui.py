#! /usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Aplicación de centro de control para el sistema de semaforización.
Se encarga de conjugar Twsited con PyQt4 mediante el reactor de Qt.
Define mediante la constante APP_NAME la ubicación del archivo de
configuración en el sistema.
'''


import sys, os
sys.path.append('..')   # Correccion de path

if not "-nopsyco" in sys.argv:
    # Psyco es un acelerador de bytecode de python.
    try:  
        import psyco
        psyco.full()
        print "Usando acelerador Psyco."
    except ImportError, e:
        pass

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from pyscada.gui.logwin import LogWin   # La gui
from pyscada.gui.twisted_app import QTwistedApp
from pyscada.gui.confdlg import ConfigDialog
from config import Config
from pyscada.gui.qt_dbhelp import build_db_url, dburl_to_qsqldb
from twisted.python import log
from pyscada.gui.login import DialogLogin

# Manejo de excepciones
import traceback
def handle_exception(exc_type, exc_value, exc_traceback):
    #TODO: Seguir acá
    text = traceback.format_exc()
    try:
        filename, line, dummy, dummy = traceback.extract_tb(exc_traceback).pop()
    except IndexError, e:
        QMessageBox.critical(None, "ERROR", "<b>%s</b> " % text.replace('\n', '<br />'))
    else:   
        filename = os.path.basename(filename)
        error = "%s: %s" % (str(exc_type).split(".")[-1], exc_value)

        QMessageBox.critical(None, "ERROR", "<b>%s</b> " % error + "on line %d, file %s" % (line, filename))

#sys.excepthook = handle_exception

# Alchemy
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from model import metadata

class MainTwistedApp(QApplication):
    ''' 
    Aplicacion principal, reune configuración.
    Sobre esta clase se emiten los eventos:
    
     * data_available(co, uc, svs, dis, svs, evs).
    
    '''
    # Este nombre determina el nombre de la carpeta donde se guarda
    # la configuracion.
    scada = None
    _db_con = None
    _db_url = None
    _sa_engine = None
    _SessionClass = None
    
    def __init__(self, args):
        QApplication.__init__(self, args) # Superconstructor
        
        # Instalacion del reactor para Qt4
        from lib.twisted.qtreactor import qt4reactor #@UnresolvedImport
        qt4reactor.install()
        # Configuracion de los loggers
        self.setup_logger()
        self.setup_config()
        
        # Twisted
        try:
            from twisted.internet import reactor
            # GUI, debe ser luego de importar twisted
            login = DialogLogin(None)
            
            if login.exec_():
                self.pixmap_splash = QPixmap(':/res/splash/splash.png')
                self.splash = QSplashScreen( self.pixmap_splash )
                self.splash.show()
                from pyscada.gui.scadamw import ScadaMainWin
                self.config_dlg = ConfigDialog()
                
                self.win = ScadaMainWin()
                
                self.splash.finish(self.win)
                self.connect(self.win, SIGNAL('closed()'), reactor.stop) #@UndefinedVariable
                
                # qApp.instance().emit(SIGNAL('data_available'), co, uc, svs, dis, ais, evs)
                #self.connect(self, SIGNAL('data_available'), self.mostrar )
                # Screenshots
                self.win.menuAdmin.setVisible(False)
        except Exception, e:
            self.log(e)
            
    def mostrar(self, co, uc, svs, dis, ais, evs):
        self.log('Datos recibidos %s' % [co, uc, svs, dis, ais, evs ] )
    
    def db_url(): #@NoSelf
        doc = """Url""" #@UnusedVariable
       
        def fget(self):
            
            if not self._db_url:
                self.log('Generando URL de ceonxion')
                self._db_url = build_db_url( **dict(self.cfg.scada) )
                self.log(self._db_url)
            return self._db_url

        return locals()
       
    db_url = property(**db_url())
    
    def sa_engine(): #@NoSelf
        def fget(self):
            if not self._sa_engine:
                self._sa_engine = create_engine(self.db_url)
                self._sa_engine.connect()
            return self._sa_engine
        return locals()
    sa_engine = property( **sa_engine() )
    
    def SessionClass(): #@NoSelf
        def fget(self):
            if not self._SessionClass:
                if not metadata.bind:
                    metadata.bind = self.sa_engine
                self._SessionClass = sessionmaker( bind = self._sa_engine )
            return self._SessionClass
        return locals()
    SessionClass = property( **SessionClass() )
    
    def db_con(): #@NoSelf
        doc = """Conexion Qt a la base de datos""" #@UnusedVariable
       
        def fget(self):
            if not self._db_con:
                self.log('Iniciando conexion Qt con la base de datos')
                try:
                    self._db_con = dburl_to_qsqldb( self.db_url )
                except Exception, e:
                    QMessageBox.critical(None, "Error", u"""
                    
                    <h2>Error en la base de datos</h2>
                    <p>Por favor reconfigure la conexión con la base de datos 
                    y reinicie la aplicación.</p>
                    
                    <p>%s</p>
                    """ % e)
                # sys.exit(3)
            return self._db_con
           
        def fset(self, value):
            assert type(value) == QSqlDatabase, "Conexion erronea"
            self._db_con = value
            # Emitir la señal para que la aplicación refresque en funcion
            # de la nueva base de datos.
            self.emit(SIGNAL('dbConnectionChanged(QSqlDatabase*)'), value)
        return locals()
    db_con = property(**db_con())
    
    
    def setup_config(self):
        try:
            self.cfg = Config('config.cfg')
        except IOError:
            self.log('ALERTA: Creando configuracion vacía')
            self.cfg = Config()
        else:
            self.log('Confó: OK')
    
    def setup_logger(self):
        ''' Basicamente logueamos todo'''
        from twisted.python import log
        # De esta manera podemos utilizar ipdb
        log.startLogging(sys.stdout, setStdout=False )
    
    def log(self, msg):
        ''' Wrap de python log '''
        from twisted.python import log
        log.msg(msg)
        
    def error(self, err):
        ''' Wrap de python error '''
        from twisted.python import log
        log.err(err)
    
    def finalize(self):
        # Guardamos el archivo de configuracion
        try:
            self.cfg.save(open('config.cfg', 'w'))
        except Exception, e:
            self.error(e)
            self.error('Error guardando la configuracion %s' % self.__config_filename)
        else:
            self.log('Guardando configuración con exito')
        self.log('Finalizando')
    
    
    def exec_(self):
        from twisted.internet import reactor
        try:
            self.win.show()
        except AttributeError, e:
            log.err('Error de inicializacion. No iniciando reactor.')
        else:
            return reactor.run() #@UndefinedVariable
    
    def quit(self):
        # Cleanup
        self.finalize()
        # Ahora cerramos la aplicacion
        from twisted.internet import reactor
        reactor.stop() #@UndefinedVariable
    
def main(argv = sys.argv):
    ''' Función main '''
    app = MainTwistedApp(argv)
    return app.exec_()

if __name__ == "__main__":
    if hasattr(sys, 'frozen') and sys.frozen: #@UndefinedVariable
        exe_dir = os.path.dirname(sys.executable)
        print "Running as executable: %s" % exe_dir
        exe_dir = os.path.dirname(sys.executable)
        if exe_dir != os.getcwd():
            print "Cambio de path"
            os.chdir(exe_dir)
    else:
        print "Running as script"
    sys.exit(main())



# algpo
