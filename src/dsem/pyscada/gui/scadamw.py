#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from qscada import ScadaClientFactoryQEvents
from picnet.proto import Paquete

import sys
from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
from PyQt4.QtSql import * #@UnusedWildImport

from ui_scadamw import Ui_MainWindow

from pyscada.qscada import PicnetSCADAProtocolQEvents
from pyscada.scada import SCADAEngine
from pyscada.model import metadata
from pyscada.gui.mapview import EditingView, EditingScene , RasterLayerMap
from pyscada.scada import PicnetSCADAProtocolFactory
from pyscada.gui.zmultilayer import EditorMainWindow, MultilayeredScene
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from pyscada.gui.qt_dbhelp import dburl_to_qsqldb, PyQSqlQuery
from pyscada.gui.print_dlg import PrintDialog
from config import Config
from pyscada.gui.db_tables import EventoColorBgSqlQueryModel
from twisted.python import log
from twisted.internet import threads

def generar_reporte(template):
    win = PrintDialog()
    win.template = template
    try:
        win.exec_()
    except Exception, e:
        QMessageBox.critical(None, "Error de impresion", 
                             "Error %s" % e)


class ScadaMainWin(QMainWindow, Ui_MainWindow):
    '''
    Ventana principal de la aplicacion.
    '''
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.setup_gui()
        # Instanciamos el scada y lo dejamos listo para correr
        self.setup_scada()
        
        self.tabs.setCurrentIndex(0)
        # La solapa habilitada por defecto es la de configuración de concentra-
        # dores y unidades de control
        self.toolBox_configuracion_comandos.setCurrentIndex(1)
        # Ocultamos el zoom
        self.toolBar_mapa_visor.hide()
        self.toolBar_debug.hide()
        # Quizás podríamos cargar los mapas en segundo plano para
        # acelerar el arranque de la aplicación
        #reactor.callLater(0.1, self.load_default_map)
        
        self.connect_db_deferred()
    
    def setup_scada(self):
        #self.scada = SCADAEngine()
        #self.scada.factory.protocol = PicnetSCADAProtocolQEvents
        self.scada = ScadaClientFactoryQEvents(qApp.instance().cfg)
        
        self.scada.db_engine = 'mysql://dsem:passmenot@localhost:3306/dsem'
        
    def setup_gui(self):
        ''' Configuración de la GUI '''
        # Creamos la escena del mapa.
        self.raster_map = RasterLayerMap(self)
        try:
            rect = self.raster_map.identity_pixmap_rect
            self.map_scene = EditingScene(rect.x(), rect.y(),
                                          rect.width(), rect.height(),
                                          self)
        except Exception, e:
            print e, type(e)
        self.graphicsViewMap.setScene(self.map_scene)
        self.graphicsViewMap.raster_map = self.raster_map
        
        try:
            self.toolBar_mapa_visor.addAction(self.graphicsViewMap.actionZoomIn)
        except Exception, e:
            print e, type(e)
            
        self.map_editor = EditingView()
        
        self.map_editor.raster_map = self.raster_map
        self.map_editor.setScene(self.map_scene)
        
        # Dock
        self.dockDebugIO = DebugIODockWidget(self)
        self.dockDebugIO.hide()
        self.addDockWidget( Qt.BottomDockWidgetArea, self.dockDebugIO)
        
        
        
    @pyqtSignature('bool')
    def on_actionIO_toggled(self, checked):
        if checked:
            self.dockDebugIO.show()
        else:
            self.dockDebugIO.hide()
    
    @pyqtSignature('')
    def on_actionImprimir_triggered(self):
        #threads.deferToThread(generar_reporte, 'templates/report.html')
        win = PrintDialog(self)
        try:
            win.template = qApp.instance().cfg.reports.template
        except Exception, e:
            QMessageBox.critical(None, "Error", "No se encuentra el temaplte, verifique la configuracion (%s)" % e)
        else:
            win.exec_()
        
        
    def setupUi(self, main_window):
        Ui_MainWindow.setupUi(self, main_window)
        # Más inicialización de la GUI
        for i in range(1,64):
            self.comboPgmZona.addItem('%d' % i, QVariant(i))
            self.comboPgmUc.addItem('%d' % i, QVariant(i))
        
        self.comboPgmZona.addItem('Todas', QVariant(255))
        self.comboPgmUc.addItem('Todas', QVariant(255))
    
    def scada_start(self):
        '''
        Lo que hacemos es configurar...
        '''
        print "Iniciando SCADA"
        cfg = qApp.instance().cfg
        # Puerto TCP 
        try:
            self.scada.tcp_port = cfg.picnet.tcp_port
        except:
            if not hasattr(cfg, 'picnet'):
                cfg.picnet = Config()
            self.scada.tcp_port = cfg.picnet.tcp_port = 9761
        # Descripcion de la base de datos
        self.scada.metadata = metadata
        
        # Verborragia minima
        try:
            self.scada.verbosity = cfg.scada.verbosity
        except:
            if not hasattr(cfg, 'scada'):
                cfg.scada = Config()
            self.scada.verbosity = cfg.scada.verbosity = 1
        
        try:
            self.scada.id_rs485 = cfg.picnet.id_rs485
        except:
            self.scada.id_rs485 = cfg.picnet.id_rs485 = 1
        
        # Largar el scada en un Deferred...
        scada_deferred = Deferred()
        scada_deferred.addCallback(self.scada.start)
        scada_deferred.callback(None)
    
    @pyqtSignature('int')
    def on_tabs_currentChanged(self, index):
        self.toolBar_mapa_visor.setEnabled(index == 0)
        
    
    @pyqtSignature('int')
    def on_comboPgmZona_currentIndexChanged(self, index):
        # Sacarlo afuera.
        print index
        data = self.comboPgmZona.itemData(index).toInt()[0]
        
        if data == 255:
            self.comboPgmUc.setEnabled(False)
        else:
            self.comboPgmUc.setEnabled(True)
    
    def connect_db_deferred(self):
        # Creamos el Deferred...
        deferred = Deferred()
        deferred.addCallback(self.setupEVModel)
        deferred.addCallback(self.setupCOModel)
        deferred.addCallback(self.setupUCModel)
        db = qApp.instance().db_con
        if db:
            deferred.callback( db )
    
    
    def setupEVModel(self, con):
        '''
        Setear el modelo de las tablas de eventos...
        '''
        # High Priority
        query = QSqlQuery(u"""
            SELECT
            -- Necesito el ID, anque va a estar oculto
            EV.id as ev_id,
            
            CONCAT( LPAD(CO.id_CO,2,'0'), LPAD(UC.id_UC,2, '0')) COID,
            EV.tipo Tipo,
            EV.prio Prioridad,
            
            UC.nombre_uc Nombre, 
            EV_Descripcion.descripcion Descripción,
            
            -- EV.codigo Codigo,
            EV.nro_port `Puerto/Movi`,
            EV.nro_bit `Lamp/Bit`,
            EV.estado_bit Estado,
            
            -- Concatenar los Timestamp con los milisegundos
            -- CONCAT(DATE_FORMAT(EV.ts_bit, '%Y/%m/%d %h:%i:%s'), '.',
                -- Milisegundos padeados hacia la derecha
                -- rpad(left(EV.ts_bit_ms, 4), 4, '0') )Timestamp,
            -- Sin miliesgundos
            EV.ts_bit,
            -- Para los colores
            ts_a,
            ts_r
            
            FROM (( EV INNER JOIN UC ON EV.uc_id = UC.id ) 
                -- Es un left join de manera que si no existe Descripcion == se muestra 
                LEFT JOIN EV_Descripcion ON EV.tipo = EV_Descripcion.tipo
                    AND EV.codigo = EV_Descripcion.codigo ) 
            INNER JOIN CO WHERE co_id = CO.id_CO AND EV.prio < 2
            ORDER BY EV.atendido, EV.ts_bit DESC, EV.ts_bit_ms DESC
            """, con)
        if query.lastError().type() != QSqlError.NoError:
            raise Exception('Falla en la DB: %s' % query.lastError().databaseText())
        
        #model = QSqlQueryModel(self.tableHighPrio)
        model = EventoColorBgSqlQueryModel(self.tableHighPrio)
        model.setQuery(query)
        model.sort(model.record().indexOf('ts_bit'), Qt.DescendingOrder)
        self.tableHighPrio.setModel( model )
        self.tableHighPrio.hideColumn( model.record().indexOf('ev_id') )
        
        # Renombrar las columnas que usamos
        model.setHeaderData(model.record().indexOf('ts_a'), Qt.Horizontal, QVariant(u'Atención'))
        model.setHeaderData(model.record().indexOf('ts_r'), Qt.Horizontal, QVariant(u'Reparación'))
        
        #self.tableEventos.setModel(model)
        self.tableHighPrio.resizeColumnsToContents()
        self.tableHighPrio.resizeRowsToContents();

        # Low Priority
        query = QSqlQuery(u"""
            SELECT
            
            CONCAT( LPAD(CO.id_CO,2,'0'), LPAD(UC.id_UC,2, '0')) COID,
            EV.tipo Tipo,
            EV.prio Prioridad,
            
            UC.nombre_uc Nombre, 
            EV_Descripcion.descripcion Descripción,
            
            -- EV.codigo Codigo,
            EV.nro_port `Puerto/Movi`,
            EV.nro_bit `Lamp/Bit`,
            EV.estado_bit Estado,
            -- Concatenar los Timestamp con los milisegundos
            -- CONCAT(DATE_FORMAT(EV.ts_bit, '%Y/%m/%d %h:%i:%s'), '.',
                -- Milisegundos padeados hacia la derecha
                -- rpad(left(EV.ts_bit_ms, 4), 4, '0') )Timestamp
            EV.ts_bit
            
            FROM (( EV INNER JOIN UC ON EV.uc_id = UC.id ) 
                -- Es un left join de manera que si no existe Descripcion == se muestra 
                LEFT JOIN EV_Descripcion ON EV.tipo = EV_Descripcion.tipo 
                    AND EV.codigo = EV_Descripcion.codigo ) 
            INNER JOIN CO WHERE co_id = CO.id_CO AND EV.prio >= 2
            ORDER BY EV.ts_bit DESC, EV.ts_bit_ms DESC
            """, con)
        if query.lastError().type() != QSqlError.NoError:
            raise Exception('Falla en la DB: %s' % query.lastError().databaseText())
        model = QSqlQueryModel( self.tableLowPrio )
        model.setQuery(query)
        model.sort(model.record().indexOf('ts_bit'), Qt.DescendingOrder)
        
        self.tableLowPrio.setModel( model )
        
        self.tableLowPrio.resizeColumnsToContents()
        self.tableLowPrio.resizeRowsToContents()
        
        self.connect(qApp.instance(), SIGNAL('data_available'), self.refresh_EV)
        return con
    
    def refresh_EV(self, *largs):
        self.tableHighPrio.do_update()
        self.tableLowPrio.do_update()
        #query = self.tableHighPrio.model().query()
        #query.exec_()
        #self.tableHighPrio.model().setQuery( query )
        
        #query = self.tableLowPrio.model().query()
        #query.exec_()
        #self.tableLowPrio.model().setQuery( query )
        qApp.instance().log('Refrescando eventos en el listado')
        #print largs
    
    
    def setupCOModel(self, con):
        model = QSqlTableModel(self.tableCO, con)
        
        model.setTable('CO')
        model.select()
        self.tableCO.setModel(model)
        
            
        self.tableCO.resizeColumnsToContents()
        self.tableCO.resizeRowsToContents()
        return con
    
    def setupUCModel(self, con):
        model = QSqlRelationalTableModel(self.tableUC, con)
        model.setTable('UC')
        
#        relation = QSqlRelation('CO', 'id_CO', 'id_CO')
#        print relation
#        model.setRelation( model.fieldIndex('co_id'), 
#                           relation
#                          )
        #print model.lastError()
        #print model.lastError().databaseText()
        model.select()
        
        
        self.tableUC.setModel(model)
        self.tableUC.resizeColumnsToContents()
        self.tableUC.resizeRowsToContents()
        
        self.toolAddUC.setDefaultAction(self.tableUC.actionAddUC)
        #self.toolFilterReset.setDefaultAction(self.tableUC.actionFilterReset)
        self.tableCO.tableUC = self.tableUC
        self.connect( qApp.instance(), SIGNAL('uc_changed'), self.tableUC.update )
        
        
        return con
    
    @pyqtSignature('')
    def on_pushAddCO_pressed(self):
        model = self.tableCO.model()
        #model.insertRow(model.rowCount())
        model.insertRecord(-1, QSqlRecord())
        
    @pyqtSignature('')
    def on_pushRemoveCO_pressed(self):
        #model = self.tableCO.model()
        indexes = self.tableCO.selectedIndexes()
        log.msg(str( indexes))
        
        
    @pyqtSignature('')
    def on_actionLog_triggered(self):
        qApp.instance()
        
    
    def load_default_map(self):
        # TODO: Cargarlo de un archivo de configuracion
        #self.scene.loadFile('mapa_trelew.tar')
        pass
    
    def statusbarProgressLoading(self, progress):
        self.statusbar.showMessage('Carga de mapa %.f%%' % progress)
    
    @pyqtSignature('')
    def on_actionMapa_triggered(self):
        if self.map_editor.isHidden():
            self.map_editor.show()
            qApp.instance().setActiveWindow(self.map_editor)
        else:
            self.map_editor.hide()
        
    @pyqtSignature('')
    def on_actionQuit_triggered(self):
        qApp.instance().quit()
    
    @pyqtSignature('')
    def on_actionDBUrl_triggered(self):
        QMessageBox.information(self, "URL", '''
        <h4>La url de conexion es la siguiente</h4>
        <p>%s</p>
        ''' % self.config_dlg.dburl)
        
    def closeEvent(self, event):
        ''' Para cerrar la aplicacion cuando se cierra la ventana '''
        qApp.instance().quit()
    
    @pyqtSignature('')
    def on_actionSCADA_Config_triggered(self):
        qApp.instance().config_dlg.exec_()
        
    
    @pyqtSignature('')
    def on_actionAbout_Qt_triggered(self):
        qApp.aboutQt()
        
    @pyqtSignature('')
    def on_actionAbout_triggered(self):
        QMessageBox.about(self, self.trUtf8("Sobre Avrak"),
                          self.trUtf8('''
            <h3>HMI de Semaforización basado en µCNet</h3>
            <p>Sistema de semaforización <b>Avrak</b> basado en el motor de
             adquisición de datos <b>Alsvid</b>.</p>
            <p>Este software se rige por la licencia
            <a href="http://gnu.org/">GPL</a></p>
            <p>
                Avrak utiliza las librerías:
                <ul>
                    <li>Python (PSF)</li>
                    <li>Twisted (Divmod)</li>
                    <li>Qt4 (Nokia/Trolltech)</li>
                    <li>PyQt4 (Riverbank Computing)</li>
                    <li>Reactor Twsited PyQt4</li>
                    <li>MySQL (Sun Microsystems)</li>
                    <li>PyInstaller (develer.net)</li>
                    <li>XHTMLTOPDF(pisa)</li>
                    <li>Jinja2</li>
                    <li>python-dateutils</li>
                </ul>
            </p>
                            '''))
    @pyqtSignature('bool')
    def on_actionStart_toggled(self, start):
        if start:
            self.scada_start()
        else:
            self.scada.stop()
    
    #def on_actionStart_triggered(self):
    
    #@pyqtSignature('bool')
    def on_actionScadaToolbar_toggled(self, checked):
        print "Toolbar"
        if checked:
            self.scadaToolbar.show()
        else:
            self.scadaToolbar.hide()
        
    @pyqtSignature('')
    def on_actionStop_triggered(self):
        #self.scada.stop()
        #QMessageBox.information(self, "No funciona", "No funciona :)")
        self.scada.stop()
        
    
    def on_actionLimpiar_Eventos_triggered(self):
        print "Borrando eventos"
        for m in (self.tableHighPrio.model(), self.tableLowPrio.model()):
            if m:
                pass
                
    
    @pyqtSignature('')
    def on_pushNewCon_pressed(self):
        i = QInputDialog.getInteger(self, "ID", "ID", 5, 2, 63)
        
        if i:
            p = self.treeCons.selectedItems() and self.treeCons.selectedItems()[0] or self.treeCons  
            QTreeWidgetItem(p, ["Nuevo concentrador %d" % i[0] ])
    
    
    def on_toolBox_configuracion_comandos_currentChanged(self, index):
        '''
        Cambio de pestaña en la configuracion
        '''
        if index == 0:
            # El index 0 es el de los comandos
            
            if not isinstance(self.comboBox_concentrador.model(), QSqlQueryModel):
                # Creamos el modelo de la consulta
                model = QSqlQueryModel( self.comboBox_concentrador )
                self.comboBox_concentrador.setModel(model)
                log.msg('Creando el modelo para el listado de concentradores')
            
            query = QSqlQuery()
            ok = query.exec_("""SELECT CONCAT(id_CO, ' - ', COALESCE(ip_address, 'Sin IP'), ' (', COALESCE(nombre_co, ''), ')') `co`, 
                        id_CO, ip_address FROM CO""")
            log.msg('Refresco de la query: %s' % ok)
            if ok:
                self.comboBox_concentrador.model().setQuery(query)
    
    def comando_zona(): #@NoSelf
        doc = """Docstring""" #@UnusedVariable
       
        def fget(self):
            zona = self.comboPgmZona.itemData(self.comboPgmZona.currentIndex())
            return zona.toInt()[0]
           
#        def fset(self, value):
#            self._comando_zona = value
        return locals()
       
    comando_zona = property(**comando_zona())
    
    def comando_uc(): #@NoSelf
        doc = """Docstring""" #@UnusedVariable
       
        def fget(self):
            uc = self.comboPgmUc.itemData(self.comboPgmUc.currentIndex())
            return uc.toInt()[0]
           
#        def fset(self, value):
#            self._comando_uc = value
        return locals()
       
    comando_uc = property(**comando_uc())
    
    def on_pushButton_prog_auto_pressed(self):
        scada = qApp.instance().win.scada
        if not scada.connected:
            QMessageBox.information(None, "Conexion", "Debe estar conectado para enviar comandos")
        ip = self.comboBox_concentrador.get_col_value(2)
        # CMD ZONA MANUAL(01) PGM (00)
        pkg = Paquete.crear_paquete_comando_custom(0x01, self.comando_uc, 0x10, [ self.comando_zona, 0x00, 0x00 ] )
        if not scada.clients.has_key(ip):
            QMessageBox.information(None, "Conexion", "No se puede contactar el concentrador")
        else:
            # Creamos el paquete, que lo mande el scada
            scada.clients[ ip ].append_to_buffer(pkg)
        
    def on_pushButton_prog_manual_pressed(self):
        scada = qApp.instance().win.scada
        if not scada.connected:
            QMessageBox.information(None, "Conexion", "Debe estar conectado para enviar comandos")
        
        ip = self.comboBox_concentrador.get_col_value(2)
        # CMD ZONA MANUAL(01) PGM (00)
        pkg = Paquete.crear_paquete_comando_custom(0x01, self.comando_uc, 0x10, [ self.comando_zona, 0x01, 0x00 ] )
        if not scada.clients.has_key(ip):
            QMessageBox.information(None, "Conexion", "No se puede contactar el concentrador")
        else:
            # Creamos el paquete, que lo mande el scada
            scada.clients[ ip ].append_to_buffer(pkg)
        
        
    
        
    
class DebugIODockWidget(QDockWidget):
    '''
    Dock para el debug de la entrada salida por el socket en bytes del protcolo
    interpretados en HEX.
    '''
    
    class AutoScrollQTextEdit(QTextEdit):

        def insertPlainText(self, text):
            
            val =  QTextEdit.insertPlainText(self, text)
            
            
            return val
        
    def __init__(self, parent = None):
        QDockWidget.__init__(self, "Debug IO", parent)
        self.setAllowedAreas( Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea )
        
        widget = DebugIODockWidget.AutoScrollQTextEdit(self)
        widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
        widget.setReadOnly(True)
        self.setWidget(widget)
        self.connect(qApp.instance(), SIGNAL('data_received'), widget.insertPlainText)
    

    def hideEvent(self, event):
        self.parent().actionIO.setChecked(False)
        QDockWidget.hideEvent(self, event)
        
    
        