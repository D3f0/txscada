#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
Aplicacion twisted que utiliza el reactor de Qt4.
Se encarga de guardar la configuracion en un archivo ini
y de proveer logging.
'''
all = ('QTwistedApp',)


import sip  # PyInstaller
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject, SIGNAL
import os, sys
# Configuracion en un ini
from ConfigParser import SafeConfigParser, NoSectionError

class ScadaConfigParser(SafeConfigParser):
    '''
    Cuando una seccion no exite, se crea
    '''

    def get(self, section, option, default = None, insert_on_fail = True):
        '''
        @param insert_on_fail: Si no existe la entrada en la seccion la crea
        '''
        if not self.has_section(section) or not self.has_option(section, option):
            if insert_on_fail:
                self.set(section, option, default)
            return default
        return SafeConfigParser.get(self, section, option)

    def set(self, section, option, value):
        try:
            return SafeConfigParser.set(self, section, option, value)
        except NoSectionError:
            self.add_section(section)
            return SafeConfigParser.set(self, section, option, value)
    
class QTwistedApp(QtGui.QApplication):
    ''' Aplicación que inicropara la isntalación del reactor de PyQt4
    Una vez instanciada la plaicación se debe instanciar.
    
    Responsabilidades:
        * Crear el sistema de logging
        * Cargar la confiugracion inicial
        * Instalar el reactor qt:
            - Los imports del reactor y el protocolo deben hacerse
            luego de instanciar la aplicación.
    '''
    # Este nombre determina el directorio de configuracion, por lo tanto es
    # necesario extender la aplicación y redefinir al menos APP_NAME para 
    # utilizar otro directorio para la configuracion.
    APP_NAME = 'Q4TwsitedApp'
    
    def __init__(self, args):
        QtGui.QApplication.__init__(self, args) # Superconstructor
        
        # Instalacion del reactor para Qt4
        from lib.twisted.qtreactor import qt4reactor #@UnresolvedImport
        qt4reactor.install()
        
        self.setup_logger()
        self.setup_config()
        
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
        
    
    @staticmethod
    def pmkdir(filename):
        """Create directory components in filename. Similar to Unix "mkdir -p"."""
        components = filename.split(os.sep)
        aggregate = [os.sep.join(components[0:x]) for x in xrange(1, len(components))]
        aggregate = ['%s%s' % (x, os.sep) for x in aggregate] # Finish names with separator
        for dir in aggregate:
            if not os.path.exists(dir):
                os.mkdir(dir)
    
    def setup_config(self):
        '''Inicializa la configuración desde el archivo de configuracion'''
        from twisted.python import log
        if os.environ.has_key('APPDATA'):
            # Windows
            base_path = os.environ['APPDATA'] 
        elif os.path.expanduser('~'):
            # Linux
            base_path = os.path.expanduser('~')
        else:
            log.err('No existe el path')
        
        base_path = os.path.join(base_path, '.config', self.APP_NAME, 'config.ini')
            
        self.pmkdir(base_path)
        
        #log.msg('La configuracion se guarda en', base_path)
        cfg_parser = ScadaConfigParser()
        # Leemos la configuracion
        success = cfg_parser.read([base_path, ])
        if success:
            log.msg('Lectura exitosa de: %s' % success)
        self.__cfg_parser = cfg_parser
        self.__config_filename = base_path
    
    config = property(lambda self: self.__cfg_parser, doc="Objeto de configuracion")    
        
    def finalize(self):
        # Guardamos el archivo de configuracion
        try:
            fp = file(self.__config_filename, 'w')
            self.__cfg_parser.write(fp)
        except Exception, e:
            self.error(e)
            self.error('Error guardando la configuracion %s' % self.__config_filename)
        self.log('Finalizando')
    
    
    def exec_(self):
        from twisted.internet import reactor
        self.win.show()
        return reactor.run()
    
    def quit(self):
        # Cleanup
        self.finalize()
        # Ahora cerramos la aplicacion
        from twisted.internet import reactor
        reactor.stop()
        
sys.path += ['../..', '..' ]

def main(argv = sys.argv):
    ''' Funcion de prueba para el reactor de Qt
    '''
    app = QTwistedApp(argv)
    from twisted.internet import reactor
    win = QtGui.QWidget()
    win.setWindowTitle('Probando reactor')
    # Seteamos la geometría de la ventana
    win.setGeometry(400,100,400,100)
    win.setLayout(QtGui.QVBoxLayout())
    l = QtGui.QLabel('<h2>Test de QtReactor</h2>')
    win.layout().addWidget(l)
    win.show()
    reactor.callLater(2, lambda _: l.setText('reactor.callLater(2)'), None)
    reactor.callLater(4, reactor.stop)
    reactor.run()
    app.finalize()
    
if __name__ == "__main__":
    sys.exit(main())
