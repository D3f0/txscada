#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from config import Config
from pyscada.gui.qt_dbhelp import build_db_url
from ui_confdlg import Ui_Dialog
import re

DB_PORTS = {
    'mysql':            3306,
    'oracle':           1532,
    'postgres':         5432,
    'ms sql server':    1433,
}

DB_RFC1738_URL = {
    'ms sql server': 'mssql'
}

class ConfigDialog(QDialog, Ui_Dialog):
    '''
    Dialogo de configracion
    '''
    def __init__(self, parent = None):
        try:
            QDialog.__init__(self, parent)
            self.setupUi(self)
            
            # SpinBoxes & lineEdits
            self.connect(self.pushBrowse, SIGNAL('enabled(bool)'), self.spinPort.setEnabled )
            self.connect(self.pushBrowse, SIGNAL('enabled(bool)'), self.lineUser.setEnabled )
            self.connect(self.pushBrowse, SIGNAL('enabled(bool)'), self.linePass.setEnabled )
            self.connect(self.pushBrowse, SIGNAL('enabled(bool)'), self.lineServer.setEnabled )
            # Labels
            self.connect(self.pushBrowse, SIGNAL('enabled(bool)'), self.labelUser.setEnabled )
            self.connect(self.pushBrowse, SIGNAL('enabled(bool)'), self.labelPort.setEnabled )
            self.connect(self.pushBrowse, SIGNAL('enabled(bool)'), self.labelPass.setEnabled )
            self.connect(self.pushBrowse, SIGNAL('enabled(bool)'), self.labelServer.setEnabled )
        except Exception, e:
            import traceback
            print traceback.format_exc(1000)
            print e, 
        
    @pyqtSignature('QString')
    def on_comboDBType_currentIndexChanged(self, text):
        # Cada base de datos tiene un puerto por defecto
        # lo tomamos de /etc/services y está definido en la constante
        # DB_PORTS
        db = str(text).lower()
        if DB_PORTS.has_key(db):
            
            self.pushBrowse.setEnabled(True)
            self.port = DB_PORTS[db]
        else:
            self.pushBrowse.setEnabled(False)
    
    @pyqtSignature('')
    def on_pushBrowse_pressed(self):
        f = QFileDialog.getOpenFileName(self, 'Base de datos', '')
        if f:
            self.dbname = f
    
    
    def dbtype(): #@NoSelf
        doc = "Retorna el tipo de la base de datos"
        
        def fget(self):
            text = str(self.comboDBType.currentText()).lower()
            return re.subn(r'\(.*\)', '', text)[0].strip()
        
        def fset(self, value):
            
            index = self.comboDBType.findText(value, Qt.MatchStartsWith)
            if index < 0:
                qApp.instance().log('No se encontro la base %s' % value)
            else:
                self.comboDBType.setCurrentIndex(index)
        
        return locals()
    dbtype = property(**dbtype())
    
    
    def dbname(): #@NoSelf
        doc = """Nombre de la base de datos""" #@UnusedVariable
        def fget(self):
            return str(self.lineDBName.text())
           
        def fset(self, value):
            self.lineDBName.setText(value)
            self.emit(SIGNAL('dbnameChanged(QString)'), value)
        return locals()
       
    dbname = property(**dbname())
    
    def user(): #@NoSelf
        doc = """DB Username""" #@UnusedVariable
       
        def fget(self):
            if self.lineUser.isEnabled():
                return str(self.lineUser.text())
        def fset(self, value):
            self.lineUser.setText(value)
            self.emit(SIGNAL('userChanged(QString)'), value)
        return locals()
    user = property(**user())
    
    
    def pass_(): #@NoSelf
        doc = """DB Passwrod""" #@UnusedVariable
        def fget(self):
            if self.linePass.isEnabled():
                return str(self.linePass.text())
        def fset(self, value):
            self.linePass.setText(value)
            self.emit(SIGNAL('passChanged(QString)'), value)
            
        return locals()
    pass_ = property(**pass_())
    
    def host(): #@NoSelf
        doc = """DB Host""" #@UnusedVariable
       
        def fget(self):
            if self.lineServer.isEnabled():
                return str(self.lineServer.text())
           
        def fset(self, value):
            self.lineServer.setText(value)
            self.emit(SIGNAL('hostChanged(QString)'), value)
           
        return locals()
    host = property(**host())
    

    def port(): #@NoSelf
        doc = """DB Port""" #@UnusedVariable
       
        def fget(self):
            if self.spinPort.isEnabled():
                return self.spinPort.value()
           
        def fset(self, value):
            self.spinPort.setValue(value)
            self.emit(SIGNAL('portChanged(int)'), value)
        return locals()
    port = property(**port())
    
    def options(): #@NoSelf
        doc = """DB Options""" #@UnusedVariable
       
        def fget(self):
            return str(self.lineOptions.text())
           
        def fset(self, value):
            self.lineOptions.setText(value)
            self.emit(SIGNAL('optionsChanged(QString)'), value)
           
        return locals()
       
    options = property(**options())
        
        
    def dburl(): #@NoSelf
        doc = """
        Retorna la URL de la base para SQLAlchemy    
        """ #@UnusedVariable
       
        def fget(self):
            return build_db_url(self.dbtype, self.dbname, self.user, self.pass_, 
                                self.host, self.port, self.options)
        return locals()
    dburl = property(**dburl())
    
    #===========================================================================
    #    parametros de pincnet
    #===========================================================================
    def tcp_port(): #@NoSelf
        doc = """Puerto TCP""" #@UnusedVariable
        def fget(self):
            return self.spinPicnetTcpPort.value()
        def fset(self, value):
            self.spinPicnetTcpPort.setValue(value) 
           
        return locals()
    tcp_port = property(**tcp_port())
    
    def exec_(self):
        self.tabWidget.setCurrentIndex(0)
        cfg = qApp.instance().cfg
        
        try:
            self.dbtype = cfg.scada.type
        except Exception, e:
            print e
            if not hasattr(cfg, 'scada'):
                cfg.scada = Config()
            self.dbtype = cfg.scada.type = 'mysql'
        try:
            self.user = cfg.scada.user
        except:
            self.user = cfg.scada.user = 'dsem'
        
        try:
            self.pass_ = cfg.scada.password
        except:
            self.pass_ = cfg.scada.password = 'passmenot'
        
        try:
            self.host = cfg.scada.host
        except:
            self.host = cfg.scada.host = 'localhost'
        
        try:
            self.port = cfg.scada.port
        except:
            self.port = cfg.scada.port = 3306
            
        try:
            self.dbname = cfg.scada.dbname
        except:
            self.dbname = cfg.scada.dbname = 'dsem'
        
        try:
            self.options = cfg.scada.options
        except:
            self.options = cfg.scada.options = ''
        
        try:
            self.tcp_port = cfg.picnet.tcp_port
        except:
            if not hasattr(cfg, 'picnet'):
                cfg.picnet = Config()
            self.tcp_port = cfg.picnet.tcp_port
        
        QDialog.exec_(self)
        
    def accept(self):
        try:
            cfg = qApp.instance().cfg
            cfg.scada.type = self.dbtype 
            cfg.scada.user = self.user 
            cfg.scada.password = self.pass_ 
            cfg.scada.host = self.host
            cfg.scada.port = self.port 
            cfg.scada.dbname = self.dbname
            cfg.scada.dbname = self.dbname
            cfg.picnet.tcp_port = self.tcp_port
            #"cfg.picnet.tcp_port = self.tc
        except Exception, e:
            qApp.instance().log('Error %s' % e)
            
#        if self.initial_db_url != self.dburl:
#            QMessageBox.information(self, "Configuracion DB",
#                u"""
#                <h3>Cambio en la configuracion de la Base de Datos</h3>
#                <p>Para que la GUI y el motor SCADA tomen la nueva
#                configuracion de base de deatos, es eneceario reiniciar
#                la aplicación</p>""")
#        qApp.instance().config.set('db', 'dburl', self.dburl)
#        qApp.instance().config.set('picnet', 'tcp_port', str(self.spinPort.value()))
        QDialog.accept(self)
        



DBURL = re.compile('''
    (?P<type>\w*)://
    (?:(?P<user>[\w\d]+)(?:\:(?P<passwd>[\w\d]+))?\@)?
    (?:(?P<host>[\d\w\.]*))(:?(?<=:)(?P<port>\d{2,4}))?
    /
    (?P<db>[\w\d]*)
    (?P<args>\?[\w\d\=]*)?
    ''', re.VERBOSE )

def dburl_to_dict(url):
    match = DBURL.search( url )
    if match:
        return match.groupdict()
    