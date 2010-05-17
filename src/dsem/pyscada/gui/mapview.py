#! /usr/bin/env python
# -*- encoding: utf-8 -*-
'''
QGraphicsView tiene un método drawBackground y uno drawForeground.
drawBackground es interesante para dibujar el mapa, ya que es a 
nivel mapa y no a nivel escena (por lo tanto se puede cambiar
el zoom libremente a diferencia del approach con la ZMultiLayer)

'''

from PyQt4.QtGui import * #@UnusedWildImport
from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtSql import * #@UnusedWildImport
from esquina_wizard import EsquinaConfigWizard
from pyscada.gui.qt_dbhelp import PyQSqlQuery
import sys
import os
import re
from twisted.python import log
from pyscada.gui.esquina_view_dialog import Esquina_View_Dialog


try:
    from lib.states import BinaryStates
except ImportError:
    
    sys.path += ('..', '..%s..' % os.sep)
    from lib.states import BinaryStates

from pyscada.gui.gvmixins import GVAutoFitMixin, GVZoomingScrollingMixin
from pyscada.model import metadata

#log = lambda msg: qApp.instance().log(msg)

#def log(msg, *largs, **kwargs):
#    qApp.instance().log(msg, *largs, **kwargs)

#===============================================================================
# RasterLayerMap
#===============================================================================
class RasterLayerMap(QObject):
    '''
    Agrupa el mapa.
    '''
    images = []
    
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        
        self.files = []
        
        images = []
        try:
            map_cfg = qApp.instance().cfg.mapa
            if not hasattr(map_cfg, 'draw_map'):
                log.msg('No se carga el mapa por no definir mapa.draw_mapa = True')
                return
            elif not map_cfg.draw_map:
                log.msg('Carga de mapa desactivada')
                return
            else:
                log.msg('Carga de mapa activada')
            dirs = os.walk(map_cfg.dir_name)
            reg = re.compile(map_cfg.regex_files)
            for path, subpath, files in dirs:
                if path == qApp.instance().cfg.mapa.dir_name:
                    for f_name in files:
                        match = reg.match(f_name)
                        if match:
                            dpi = int(match.group('dpi'))
                            if hasattr(map_cfg, 'single_resolution') and map_cfg.single_resolution != dpi:
                                continue
                            log.msg("Cargando resolucion %d" % dpi)
                            pixmap = QPixmap(os.path.join(path, f_name))
                            log.msg(pixmap.rect())
                            images.append( (dpi, pixmap ) )
                            QApplication.processEvents()            
                    break # Por si hubiese otros directorios
                
            images.sort(lambda x, y:  cmp(x[0], y[0])) # Orden por dpi
            self.images = dict(images)
            
        except Exception,e:
            QMessageBox.critical(None, "Error en carga de mapa", """
                                 <h3>Error en carga de mapa</h3><p>%s</p><p>%s</p>
                                 """ 
                                 % (e, type(e)))
        
    def read_files(self, force = False):
        ''' Lee los archivos desde la configuración '''
        if not hasattr(qApp.instance().cfg, 'mapa'):
            log.msg('No se encuentra la seccion mapa en la configuración.')
            return
        map_cfg = qApp.instance().cfg.mapa # Alias
        
        if not hasattr(map_cfg, 'dir_name'):
            QMessageBox.information(None, "Mapa no establecido",u"""
            <p>El mapa no está establecido en el archivo de configuración.</p>
            """)
        
        if not self.files or force:
            log.msg('Cargando imagenes de mapa...')
            for path, subpaths, files in os.walk(map_cfg.dir_name):
                pass
            
    def is_valid(self):
        ''' Comprobar si el mapa se cargó bien.'''
        return len(self.images) != 0
    
    def load_initial_image(self):
        # TODO: Modularizar
        pass
    
    def identity_pixmap_rect(): #@NoSelf
        doc = "Rectangulo de la imagen 1 a 1"
        def fget(self):
            try:
                return self.images[qApp.instance().cfg.mapa.identity].rect()
            except:
                try:
                    w, h = qApp.instance().cfg.mapa.default_size
                except Exception, e:
                    log.err('Error: %s' % e)
                    return QRect(0,0,1000,1000)
                else:
                    return QRect(0,0, w, h)
                
        return locals()
    identity_pixmap_rect = property(**identity_pixmap_rect())
    
    def current_pixmap(): #@NoSelf
        def fget(self):
            return self.images[qApp.instance().cfg.mapa.identity]
        return locals()
    current_pixmap = property( **current_pixmap())
    
    def rect(): #@NoSelf
        doc = """Map Rectangle""" #@UnusedVariable
       
        def fget(self):
            return self._rect
           
        def fset(self, value):
            self._rect = value
            
        return locals()
    rect = property(**rect())
    
    def draw_rectangle(self, painter, gview, rect):
        pass

#===============================================================================
# EsquinaGraphicsItem
#===============================================================================
class EsquinaGraphicsItem(QGraphicsWidget):
    '''
    Instancias de esta clase se guardan en la DB. 
    '''
    # Constantes de clase
    HEIGHT, WIDTH = 20, 20
    BOUNDING_RECT = QRectF(0,0,WIDTH, HEIGHT)
    
    STATES = BinaryStates('''
        CREATED
        NORMAL
        EVENT
    ''')
    
    COLORES = {
        STATES.CREATED: QColor(0xA7, 0xD4, 0xFF),
        STATES.NORMAL: QColor(0x84, 0xC0, 0x78),
        STATES.EVENT: QColor(0xFF, 0x00, 0x00),
    }
    
    # Caché para el shape
    _shape = None    
    _state = STATES.CREATED    
    _press_pos = QPoint()
    _wizard = None
    _esquina_id = None
    _calles = None
    _co = None
    _uc = None
    
    
    def __init__(self, parent = None, esquina_id = -1):
        QGraphicsWidget.__init__(self, parent)
        # Inicialmente es movible y seleccionable
        self.setFlags( QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable )
        self.setup_actions()
        self.setup_menus()
        self._events = 0
        self.update_tooltip()
        self.connect(qApp.instance(), SIGNAL('event_attended(int, int)'), self.event_attended)
        QMetaObject.connectSlotsByName(self)
        
    
    
    #===========================================================================
    # Funciones gráficas
    #===========================================================================
    def paint(self, painter, options, widget):
        '''
        Dibuja el widget
        '''
        # Usamos el color del estado
        painter.setBrush( self.COLORES[ self.state ] )
        painter.drawEllipse(0,0,self.WIDTH,self.HEIGHT)
        
        # TODO: Esto debería estar en el View del editor
        if self.isSelected():
            # Si está seleccionado...
            painter.setBrush( QBrush())
            pen = QPen()
            pen.setWidthF(0.7)
            pen.setStyle(Qt.DotLine)
            painter.setPen(pen)
            painter.drawRect(self.BOUNDING_RECT)
        
        
    def boundingRect(self):
        return self.BOUNDING_RECT
    
    def shape(self):
        if not self._shape:
            self._shape = QPainterPath()
            self._shape.addEllipse(0,0, self.WIDTH, self.HEIGHT)
        return self._shape
    
    
    def state(): #@NoSelf
        def fget(self):
            return self._state
        def fset(self, value):
            
            self._state = value
            self.update_tooltip()
            self.emit(SIGNAL('stateChanged'), value) # Necesario???
            
        return locals()
    state = property(**state())
    
    def esquina_id(): #@NoSelf
        doc = """Docstring""" #@UnusedVariable
       
        def fget(self):
            return self._esquina_id
           
        def fset(self, value):
            '''
            En el setter de la propiedad
            '''
            query = PyQSqlQuery()
            query.exec_('SELECT * FROM Esquina LEFT JOIN UC ON UC.id = Esquina.uc_id WHERE Esquina.id = %d' % value)
            log.msg('SELECT * FROM Esquina LEFT JOIN UC ON UC.id = Esquina.uc_id WHERE Esquina.id = %d' % value)
            # Si existe el ID...
            #cant_filas = query.numRowsAffected()
            cant_filas = query.size()
            if cant_filas == 1:
                
                self._co = query.co_id
                self._uc = query.id_UC
                self._uc_id = query.uc_id
                #log.msg(str((self._co, self._uc)))
                query.exec_("""
                        SELECT nombre FROM Calle 
                        INNER JOIN Esquina_Calles 
                            on Calle.id = Esquina_Calles.calle_id 
                        where Esquina_Calles.esquina_id = %d;
                """ % value)
                
                calles = set()
                if query.numRowsAffected() > 0:
                    while query.next():
                        calles.add(query.nombre)
                self._calles = ', '.join(calles)
                
                self._esquina_id = value
                self.state = EsquinaGraphicsItem.STATES.NORMAL
                
                self.connect(qApp.instance(), SIGNAL('data_available'), 
                             self.listen_events)
                
                query.exec_('SELECT count(EV.id) as eventos FROM EV WHERE EV.uc_id =  %d' % self._uc_id)
                self.events = query.eventos
                log.msg('Cantidad de eventos para %d = %d' % (self._uc, self.events))
            else:
                log.err('Problemas con la esquina. Filas afectadas %d' % cant_filas)
                
                
        return locals()
       
    esquina_id = property(**esquina_id())
    
    def listen_events(self, co_id, uc_id, svs, dis, ais, evs):
        ''' Escucha los eventos que vienen desde el SCADA '''
        if self._co == co_id and self._uc == uc_id:
            cant_evs = (len(evs) / 8)
            if cant_evs:
                self.events += 1
    
    def event_attended(self, co, uc):
        ''' Ecucha la atención de eventos que viene desde la tabla '''
        if self._co == co and self._uc == uc:
            self.events -= 1
            
                
    def events(): #@NoSelf
        doc = """Contador de eventos. Cuando es cero la esquina está en verde""" #@UnusedVariable
       
        def fget(self):
            return self._events
           
        def fset(self, value):
            self._events = value
            if value > 0:
                self.state = self.STATES.EVENT
            else:
                self.state = self.STATES.NORMAL
            
            self.update()
            
        return locals()
       
    events = property(**events())
                
    
    def update_tooltip(self):
        ''' Actualizar el tooltip en funcion del estado. Es llamada en el
        setter de state '''
        if self.state == EsquinaGraphicsItem.STATES.CREATED:
            self.setToolTip('Esquina sin configurar')
        elif self.state == EsquinaGraphicsItem.STATES.NORMAL:
            self.setToolTip('''<b>COID: %.2d%.2d</b><br /> 
                                Calles: %s''' % (self._co, self._uc, self._calles, ))
        elif self.state == EsquinaGraphicsItem.STATES.EVENT:
            self.setToolTip('''<b>COID: %.2d%.2d</b><br /> 
                                Calles: %s<br />
                                <i style="color: red;">Eventos sin atender: %d<i>''' % (self._co, self._uc, self._calles, self.events))
        
        
    def setup_actions(self):
        self.actionBringToFront = QAction(self.trUtf8('Traer al fretne'), self)
        self.actionBringToFront.setObjectName('actionBringToFront')
        
        self.actionSendToBack = QAction(self.trUtf8('Enviar al fondo'), self)
        self.actionSendToBack.setObjectName('actionSendToBack')
        
        self.actionRemoveItem = QAction(self.trUtf8('Quitar Esquina'), self)
        self.actionRemoveItem.setObjectName('actionRemoveItem')
        
        self.actionLock = QAction(self.trUtf8('Bloquear'), self)
        self.actionLock.setObjectName('actionLock')
        self.actionLock.setCheckable(True)
        
        
        self.actionConfig = QAction(self.trUtf8('Configurar'), self)
        self.actionConfig.setObjectName('actionConfig')
        
    
        
    def setup_menus(self):
        self.menu = QMenu()
        self.menu.addAction(self.actionBringToFront)
        self.menu.addAction(self.actionSendToBack)
        self.menu.addSeparator()
        self.menu.addAction(self.actionLock)
        self.menu.addAction(self.actionConfig)
        self.menu.addSeparator()
        self.menu.addAction(self.actionRemoveItem)
    
    def contextMenuEvent(self, event):
        self.menu.exec_(event.screenPos())
    
    
    @pyqtSignature('')
    def on_actionBringToFront_triggered(self):
        excluded = (self.scene().background, self)
        
        items = filter( lambda item: item not in excluded, self.scene().items())
        max_z = max( map(lambda item: item.zValue(), items ))
        print max_z
        if self.zValue() != max_z:
            self.setZValue(max_z + 1)
    
    @pyqtSignature('')
    def on_actionSendToBack_triggered(self):
        excluded = (self.scene().background, self)
        items = filter( lambda item: item not in excluded, self.scene().items())
        
        min_z = min( map(lambda item: item.zValue(), items ))
        if self.zValue() != min_z:
            self.setZValue(min_z - 1)
    
    @pyqtSignature('')
    def on_actionRemoveItem_triggered(self):
        resp = QMessageBox.question(None, 'Quitar el item', 'Quitar el item?',
                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                             QMessageBox.Cancel)
        if resp == QMessageBox.Yes:
            log.msg('Se va a remover el item de la esquina de la ecene')
            self.scene().removeItem(self)
            if self.esquina_id:
                log.msg('Quitando esquina de la DB id = %d' % self.esquina_id)
                query = PyQSqlQuery()
                
                transaction = qApp.instance().db_con.transaction()
                log.msg('Inicio de la tranasccion? %s' % transaction)
                try:
                    query_es_ca = QSqlQuery('SELECT id FROM Esquina_Calles WHERE esquina_id = %d'% self.esquina_id)
                    while query_es_ca.next():
                        esquina_calles_id = query_es_ca.value(0).toInt()[0]
                        log.msg('Se van a actualizar de los semaforos con id = %d'%esquina_calles_id)
                        query.exec_( """UPDATE Semaforo SET Esquina_Calles_id = Null, 
                                                subti_mov = Null, x = Null, y = Null
                                                WHERE Esquina_Calles_id  = %d
                                    """ % esquina_calles_id)
                        
                    log.msg('Se van a borrar la Esquina_Calles')
                    query.exec_('DELETE FROM Esquina_Calles WHERE esquina_id = %d'% self.esquina_id)         
                    query.exec_('DELETE FROM Esquina WHERE Esquina.id = %d' % self.esquina_id)
                    log.msg("%s" % query.lastError().databaseText() or "OK")
                    
                    if not query.lastError().type() == QSqlError.NoError:
                        if transaction:
                            qApp.instance().db_con.rollback()
                        log.err('Error en la DB: %s' % query.lastError().databaseText())
                    else:
                        if transaction:
                            commit = qApp.instance().db_con.commit()
                            log.msg('Commit exitoso %s' % commit)
                except Exception, e:
                    log.err(str(e))
                    if transaction:
                        qApp.instance().db_con.rollback()
                
    
    @pyqtSignature('bool')
    def on_actionLock_toggled(self, locked):
        
        if not locked:
            self.setFlags(self.flags() | QGraphicsItem.ItemIsMovable)
        else:
            log.msg('Lock')
            self.setFlags(self.flags() & ~QGraphicsItem.ItemIsMovable)
            
    
    
    
    #===========================================================================
    # Ejecución del wizard.
    #===========================================================================
    @pyqtSignature('')
    def on_actionConfig_triggered(self):
        if self.state == EsquinaGraphicsItem.STATES.CREATED:
            if not self._wizard:
                self._wizard = EsquinaConfigWizard(self)
            if self._wizard.exec_():
                
                
                self.esquina_id = self._wizard.esquina_id
#                del(self._wizard)
                # Cambiamos el color
                #self.update()
            else:
                log.msg('Se cancela la edicion de esquina')
        else:
            log.msg('La esquina ya esta configurada')
            resp = QMessageBox.question(None, 'Aviso','La esquina ya esta configurada',
                             QMessageBox.Ok,
                             QMessageBox.Ok)    
            
    
    def mouseDoubleClickEvent(self, event):
        '''
        Si se hace doble click sobre un item sin configurar, se lanza el
        wizard de configuracion.
        '''
        if self.state == self.STATES.CREATED:
            self.actionConfig.trigger()
        #QMessageBox.information(None, "Esquina", "Esquina")
    
    
    
    
    def _itemChange(self, change, value):
        #print change, value
        if change == QGraphicsItem.ItemPositionHasChanged:
            print "Se movio"
        elif change == QGraphicsItem.ItemPositionChange:
            print "Movimiento"
        return value
    
    def check_boundaries(self):
        '''
        Reubica el item dentro de la escena
        '''
        scene_rect, pos, rect = self.scene().sceneRect(), self.pos(), self.boundingRect()
        new_pos = QPointF(pos)
        
        if pos.x() > scene_rect.width():
            new_pos.setX( scene_rect.width() - rect.width() )
        elif pos.x() < scene_rect.x():
            new_pos.setX( scene_rect.x()  )
            
        if pos.y() > scene_rect.height():
            new_pos.setY( scene_rect.height() - rect.height() )
        elif pos.y() < scene_rect.y():
            new_pos.setY( scene_rect.y() )
            
        if new_pos != pos:
            self.setPos(new_pos)
    
    def mouseReleaseEvent(self, event):
        '''
        Liberación de la tecla de del mouse.
        '''
        self.check_boundaries()
            
        new_pos = self.pos()
        
        if self._press_pos != new_pos and self.esquina_id:
            query = PyQSqlQuery()
            query.exec_('UPDATE Esquina SET x=%d, y=%d WHERE Esquina.id = %d' %
                        (new_pos.x(), new_pos.y(), self.esquina_id))
            if query.lastError() != QSqlError.NoError:
                log.err(str(query.lastError().databaseText()))
                
        if event.modifiers() != Qt.ShiftModifier:
            self.scene().clearSelection()    
        
        QGraphicsWidget.mouseReleaseEvent(self, event)
    
    
    def mousePressEvent(self, event):
        self._press_pos = self.pos()
        QGraphicsWidget.mouseReleaseEvent(self, event)
        
#===============================================================================
# MapBakgroundGraphicsView
#===============================================================================
class MapBakgroundGraphicsView(QGraphicsView, GVAutoFitMixin, GVZoomingScrollingMixin):
    '''
    Visualizador de QGraphicsScene con pintado de mapa.
    Agrupa QActions comunes.
    '''
    __map = None
    accept_mouse_events = False
    
    def __init__(self, parent = None):
        QGraphicsView.__init__(self, parent)
        self.setAlignment(Qt.AlignLeft | Qt.AlignRight)
        self.setRenderHint( QPainter.Antialiasing )
        self.autofit = False
        self.setup_actions()
        QMetaObject.connectSlotsByName(self)
        
    def setup_actions(self):
        self.actionZoomIn = QAction('Zoom In', self)
        self.actionZoomIn.setObjectName('actionZoomIn')
        self.actionZoomIn.setShortcut('Ctrl++')
        self.actionZoomIn.setIcon(QIcon(':/icons/res/zoom-in.png'))
        
        self.addAction( self.actionZoomIn )
        
    def hideEvent(self, event):
        self.emit(SIGNAL('hide()'))
        QGraphicsView.hideEvent(self, event)

    def wheelEvent(self, event):
        GVZoomingScrollingMixin.wheelEvent(self, event)
        #QGraphicsView.wheelEvent(self, event)


    def mousePressEvent(self, event):
        GVZoomingScrollingMixin.mousePressEvent(self, event)
        if not self.accept_mouse_events:
            QGraphicsView.mousePressEvent(self, event)


    def mouseReleaseEvent(self, event):
        GVZoomingScrollingMixin.mouseReleaseEvent(self, event)
        if not self.accept_mouse_events:
            QGraphicsView.mouseReleaseEvent(self, event)


    def mouseMoveEvent(self, event):
        GVZoomingScrollingMixin.mouseMoveEvent(self, event)
        if not self.accept_mouse_events:
            QGraphicsView.mouseMoveEvent(self, event)
    
    @pyqtSignature('')
    def on_actionZoomIn_triggered(self):
        print "Zoom in"
        QMessageBox.information(self, "Zoom in", "Zoom In")
    
    # Setting the map
    def raster_map(): #@NoSelf
        def fget(self):
            return self.__map
        def fset(self, value):
            assert isinstance(value, RasterLayerMap), "%s no es un mapa"    
            self.__map = value
            self.current_dpi = qApp.instance().cfg.mapa.identity
            # Cuando cambiamos el mapa debemos actualizar la vista para 
            # redibujar el fondo
            self.update()
            
        return locals()
    raster_map = property( **raster_map() )
    
    def zoom(self, steps):
        
        if not self.raster_map:
            return GVZoomingScrollingMixin.zoom(self, steps)
        else:
            # TODO: Zoom
            return
            identity_dpi = qApp.instance().cfg.mapa.identity 
            dpis = self.raster_map.images.keys()
            factors = map(lambda x: (dpis, float(x) / identity_dpi), dpis)
            factor = None
            if steps > 0:
                factors.sort(lambda a, b: cmp(a[0], b[0]) )
                for i, tup in enumerate(factors):
                    if self.current_dpi == tup[0]:
                        index = i
                        break
                index = dpis.index(self.current_dpi)
                if index < len(dpis) - 1:
                    self.current_dpi = factors[ index + 1][0]
                    factor = factors[ index + 1][1]
            else:
                factors.sort(lambda a, b: cmp(a[0], b[0]), reverse = True)
                for i, tup in enumerate(factors):
                    if self.current_dpi == tup[0]:
                        index = i
                        break
                    
                if index > 0:
                    self.current_dpi = factors[ index - 1][0]
                    factor = factors[ index - 1][1]
            if factor:
                matrix = QMatrix()
                matrix.scale(factor, factor) 
                self.setMatrix(matrix)
                self.update()
                        
    
    
    def drawBackground(self, painter, rect):
        # The magic comes here
        if self.raster_map and self.raster_map.is_valid():
            #painter.save()
            #painter.resetMatrix()
            #painter.
            
            painter.drawPixmap( QPointF(rect.x(), rect.y()),
                                self.raster_map.images[ self.current_dpi ], 
                                #self.raster_map.current_pixmap, 
                                rect)
            #painter.restore()

class EditingView(MapBakgroundGraphicsView):
    '''
    Editor de mapa. Solo los usuarios privilegiados pueden modificar el mapa.
    Inicialmente implementado como un QGraphicsView, luego será un QWidget
    o un QMainWindow. 
    '''
    def __init__(self, parent = None):
        MapBakgroundGraphicsView.__init__(self, parent)
        self.setWindowTitle('Editor de mapa')
        

class MapView(MapBakgroundGraphicsView):
    '''
    Visor del mapa de la primer solapa.
    '''
    accept_mouse_events = True
    
    def __init__(self, parent = None):
        MapBakgroundGraphicsView.__init__(self, parent)
        self.current_item = None
        self.setup_actions()
        self.setup_menu()
        QMetaObject.connectSlotsByName(self)
        
    def setup_actions(self):
        MapBakgroundGraphicsView.setup_actions(self)
        self.actionIrAEsquina = QAction(self.trUtf8('Ir a esquina'), self)
        self.actionIrAEsquina.setObjectName('actionIrAEsquina')
        self.connect(self.actionIrAEsquina, SIGNAL('triggered()'), self.motrar_esquina)
        
    def setup_menu(self):
        self.menu = QMenu()
        self.menu.addAction(self.actionIrAEsquina)
        
    def mouseDoubleClickEvent(self, event):
        self.current_item = self.itemAt(event.pos())
        if self.current_item:
            self.actionIrAEsquina.trigger()
                
    def contextMenuEvent(self, event):
        self.current_item = self.itemAt(event.pos())
        
        if type(self.current_item) == EsquinaGraphicsItem:
            self.menu.exec_(self.mapToGlobal(event.pos()))
    
    
    def motrar_esquina(self):
        try:
            esquina_id = self.current_item.esquina_id
        except AttributeError:
            pass # A veces pasa
        else:
            if esquina_id > 0:
                self.esquina = Esquina_View_Dialog(None, esquina_id)
                self.connect(self.esquina, SIGNAL('closed'), self.cerrar_esquina_teimpo_real)
    
    
    def cerrar_esquina_teimpo_real(self):
        log.msg('Cerrando referencia a la ventana de tiempo real')
        del self.esquina
        

#===============================================================================
# EditingScene
#===============================================================================
class EditingScene(QGraphicsScene):
    '''
    Escena con capacidades de edicion, para generar una visor de solo lectura
    se debe captuar:
        - mouseDoubleClickEvent
        - mousePressEvent
    ...para evitar la modificacion de los items. 
    '''
    
    # Para el ordenamiento de los items de la capa de esquinas
    INITIAL_Z_INDEX = 1
    
    def __init__(self, x, y, w, h, parent = None):
        QGraphicsScene.__init__(self, x, y, w, h, parent)
        
        self.background = self.addRect(self.sceneRect())
        self.background.setZValue( -10 )
        self.current_z_index = self.INITIAL_Z_INDEX
        self._con = None
        self.load_from_db()
        
    def load_from_db(self):
        qApp.instance().log('Cargando esquinas en el mapa')
        esquina = PyQSqlQuery('SELECT * FROM Esquina', qApp.instance().db_con)
        log.msg("Cantidad de esquinas a cargar: %d" % esquina.size())
        while esquina.next():
            item = EsquinaGraphicsItem()
            item.setPos(float(esquina.x), float(esquina.y))
            
            self.addItem(item)
            # Esquina....
            item.esquina_id = esquina.id
        
        
    def mouseDoubleClickEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            pos = event.scenePos()
            item = self.itemAt(pos)
            #print item
            if not item or item == self.background:
                # No Overlap
                x, y = pos.x(), pos.y()
                item = EsquinaGraphicsItem()
                item.setPos(x - 10, y - 10)
                self.addItem(item, True)
                
                #self.update()
                #r = self.addRect(x - 10, y - 10, 40, 40, QPen(), QBrush(QColor(255,0,0)))
                #r.setFlags( QGraphicsItem.ItemIsMovable )
        QGraphicsScene.mouseDoubleClickEvent(self, event)
        
    def addItem(self, item, zorder = False):
        QGraphicsScene.addItem(self, item)
        if zorder:
            item.setZValue( self.current_z_index )
            self.current_z_index += 1
    
    

#===============================================================================
# Código de prueba
#===============================================================================
def main(argv = sys.argv):
    ''' Funcion main '''
    from pyscada.gui.twisted_app import QTwistedApp
    
    app = QTwistedApp(argv)
    class MainWin(QMainWindow):
        def closeEvent(self, event):
            from twisted.internet import reactor
            reactor.stop()
    app.win = MainWin()
    
    central_widget = QWidget()
    app.win.setCentralWidget(central_widget)
    layout = QVBoxLayout()
    
    layout.setMargin(2)
    layout.addWidget(QLabel('''
    <h3>Map View test</h3>
    <p>Checking out</p>
    '''))
    central_widget.setLayout( layout )
    viewer = MapBakgroundGraphicsView()
    scene = EditingScene(0, 0, 20000, 20000)
    checkAutofit = QCheckBox(central_widget)
    checkAutofit.setText('&Autofit')
    checkAutofit.setChecked( viewer.autofit )
    
    def set_autofit(checked):
        viewer.autofit = checked
        
    QObject.connect(checkAutofit, SIGNAL('toggled(bool)'), set_autofit )
    layout.addWidget( checkAutofit )
    
    viewer.setScene( scene )
    layout.addWidget( viewer )
    app.win.show()
    return app.exec_()
    
    
if __name__ == "__main__":
    #sys.path += ['..', '..%s..' % os.sep]
    #from
    sys.exit(main())
