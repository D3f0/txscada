#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
Segunda implementacion de el visualizador de mapas con zoom
basado en tiles.
'''

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import tarfile
import re
from lib.decos import timeit #@UnresolvedImport



def print_matrix(m):
    ''' Impresión de una matriz con sus 4 coeficientes '''
    print "[ %.2f %.2f 0 ]\n[ %.2f %.2f 0]\n[ %.2f %.2f 1]" % (m.m11(), m.m12(), 
                                                               m.m21(), m.m22(),
                                                               m.dx(), m.dy() )

class LayerPixmap(QGraphicsPixmapItem):
    '''
    Un item pixmap que intenta pintar el pixmap a su resolución original,
    tratando de no tardar demaciado
    '''
    
    IDENTITY = QMatrix() # Matriz identidad
    
    @classmethod
    def is_identity(cls, m):
        res = cls.IDENTITY.m11() == m.m11() and \
               cls.IDENTITY.m12() == m.m12() and \
               cls.IDENTITY.m21() == m.m21() and \
               cls.IDENTITY.m22() == m.m22()
        if not res:
            print "NO ES IDENTIDAD", 
            print_matrix(m)
        return res
    
    @timeit('QPainter')
    def paint(self, painter, options, widget):
        self.scene()
# *** Original ***
#    Q_D(QGraphicsPixmapItem);
#    Q_UNUSED(widget);
#
#    painter->setRenderHint(QPainter::SmoothPixmapTransform,
#                           (d->transformationMode == Qt::SmoothTransformation));
#
#    QRectF exposed = option->exposedRect.adjusted(-1, -1, 1, 1);
#    exposed &= QRectF(d->offset.x(), d->offset.y(), d->pixmap.width(), d->pixmap.height());
#    painter->drawPixmap(exposed, d->pixmap, exposed.translated(-d->offset));
#
#    if (option->state & QStyle::State_Selected)
#        qt_graphicsItem_highlightSelected(this, painter, option);


# *** Optimized ***
#  QRect exposedRect = painter.matrix().inverted()
#             .mapRect(event->rect())
#             .adjusted(-1, -1, 1, 1);
#             // the adjust is to account for half pixels along edges
#             painter.drawPixmap(exposedRect, pix, exposedRect);

        if self.is_identity( painter.matrix() ):
            #print "Matriz identidad :) :) :)"
            rect = painter.matrix().inverted()[0]
            r = rect.mapRect(options.exposedRect).adjusted( -1, -1, -1, -1)
            print r
        else:
            #print "La matriz no es la identidad :( :( :("
            pass
        
        #print_matrix(painter.matrix())
        #print_matrix( self.matrix() )
        
        exposed = options.exposedRect.adjusted(-1, -1, 1, 1)
        exposed &= QRectF(self.offset().x(), self.offset().y(), self.pixmap().width(), self.pixmap().height())
        #print exposed
        trans = exposed.translated(-self.offset())
        #print trans
        print "Width:", trans.width(), exposed.width()
        print "Height:", trans.height(), exposed.height()
         
        painter.drawPixmap(exposed, self.pixmap(), trans)
        
        #QGraphicsPixmapItem.paint(self, painter, options, widget)
        #painter.drawRect(0, 0, self.pixmap().size().width(), self.pixmap().size().height())

class SemItem(QGraphicsItem):
    # Tamaño
    WIDTH = HEIGHT = 12
    BoundingRect = QRectF(-WIDTH/2,-HEIGHT/2,WIDTH,HEIGHT)
    
    ALLOW_OVERLAP = False
    
    def __init__(self, *largs):
        '''
        Item grafico sobre el editor o visualizador. Representa un item.
        '''
        QGraphicsItem.__init__(self, *largs)
        self.menu_edit = QMenu()
        self.actionDelete = self.menu_edit.addAction('Eliminar')
        QObject.connect(self.actionDelete, SIGNAL('triggered()'), self.delete)
        
        self.menu_view = QMenu()
        self.menu_view.addAction('Configurar')
        self.menu_view.addAction('Focalizar')
        self.update()
        QInputDialog.getText(None, 'Dame una cadena', 'Dame una cadena')
        
    def delete(self):
        self.scene().removeItem(self)
        
    def paint(self, painter, options, widget):
        painter.setBrush(QBrush(QColor(0x32, 0xf3, 0x2A)))
        
        painter.drawEllipse(self.boundingRect().x(),self.boundingRect().y(),self.WIDTH,self.HEIGHT)
    
    def boundingRect(self):
        return self.BoundingRect
    
    def contextMenuEvent(self, event):
        print "Modo"
        if self.scene()._view_mode == MultilayeredViewer.View:
            self.menu_view.exec_(event.screenPos())
        else:
            self.menu_edit.exec_(event.screenPos())
    
    
        
    @classmethod
    def addOn(cls, scene, pos):
        '''
        Factory para el item, llamado desde la vista.
        '''
        if scene.itemAt(pos) and isinstance(scene.itemAt(pos), cls) and not cls.ALLOW_OVERLAP:
            return
        item = cls()
        item.setPos(pos.x(), pos.y())
        scene.addItem(item)
        
    
    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

#------------------------------------------------------------------------------
# Visor
#------------------------------------------------------------------------------
class MultilayeredViewer(QGraphicsView):
    
    # Modos
    Normal      = 0x00
    Hand        = 0x01
    Zoom        = 0x02
    Draw        = 0x03
    View        = 0x04
    
    def __init__(self, *largs):
        QGraphicsView.__init__(self, *largs)
        self._mode = self.Normal
        self._zoom = 1
        self._zoom_step = 0.2
        self._max_zoom = 2
        self._min_zoom = 0.2
        
        # Para el zoom con el boton central
        self._mousePressPos = QPoint()
        self._scrollBarValuesOnMousePress = QPoint()
        self.mode = self.View
    
    def mode(): #@NoSelf
        doc = """Modo de la escena""" #@UnusedVariable
       
        def fget(self):
            return self._mode
           
        def fset(self, mode):
            
            if mode == self._mode:
                return
            self._mode =  mode
            if mode == self.Normal:
                self.setDragMode( QGraphicsView.NoDrag )
            elif mode == self.Hand:
                self.setDragMode( QGraphicsView.ScrollHandDrag )
            elif mode == self.Zoom:
                pass
            self.emit(SIGNAL('modeChanged(int)'), mode)
            print "Modo:", self.mode_str
           
        return locals()
       
    mode = property(**mode())
    
    def zoom(): #@NoSelf
        doc = """Zoom""" #@UnusedVariable
       
        def fget(self):
            return self._zoom
           
        def fset(self, value):
            if value < self.max_zoom and value > self.min_zoom:
                self._zoom = value
                self.setMatrix(QMatrix().scale(value, value))
                self.emit(SIGNAL('zoomChanged(float)'), value)
            # Si el zoom se va por arriba o debajo de lo permitido, no cambiamos
        return locals()
    zoom = property(**zoom())

    
    def _get_mode_str(self):
        # FEO, FEO, FEO!!!!
        return filter(lambda x: x[1] == self.mode, self.__class__.__dict__.items())[0][0]
    
    mode_str = property(_get_mode_str, doc = "Nombre del modo")
    
    def min_zoom(): #@NoSelf
        doc = """Zoom minimo""" #@UnusedVariable
       
        def fget(self):
            return self._min_zoom
        return locals()
       
    min_zoom = property(**min_zoom())
    

    def max_zoom(): #@NoSelf
        doc = """Max zoom""" #@UnusedVariable
       
        def fget(self):
            return self._max_zoom
        return locals()
       
    def zoom_step(): #@NoSelf
        doc = """Escalon de zoom""" #@UnusedVariable
       
        def fget(self):
            return self._zoom_step
           
        return locals()
       
    zoom_step = property(**zoom_step())
    
    def mousePressEvent(self, event):
        # DEBUG
        print "Click", event.pos().x(), event.pos().y(),
        print "Escenea", self.mapToScene(event.pos()).x(), self.mapToScene(event.pos()).y()
        # DEBUG
        
        if self.mode == self.Zoom:
            btns = event.buttons()
            if btns &  Qt.RightButton and self.scene():
                self.scene().request_zoom_out()
                
            elif btns & Qt.LeftButton and self.scene():
                self.scene().request_zoom_in()
                
            print self.zoom
            m = self.matrix()
            print_matrix(m)
            
            
        elif self.mode == self.Draw:
            print "Draw"
            if event.buttons() & Qt.LeftButton:
                item = SemItem.addOn(self.scene(), self.mapToScene(event.pos()))
            
        elif self.mode == self.Hand:
            pass
        
        if event.buttons() & Qt.MidButton:
            self._mousePressPos = QPoint(event.pos())
            self._scrollBarValuesOnMousePress.setX(self.horizontalScrollBar().value())
            self._scrollBarValuesOnMousePress.setY(self.verticalScrollBar().value())

        
        QGraphicsView.mousePressEvent(self, event)
    
    def wheelEvent(self, event):
        numDegrees = event.delta() / 8
        numSteps = numDegrees / 15

        if event.orientation() == Qt.Vertical:
            self.scene_zoom(numSteps)
            print "Zoom", numSteps
        event.accept()
    
    def scene_zoom(self, mode = 1):
        '''
        Cambio de zoom, en funcion de las layers que tenga la escena
        @param mode: Si es > 0, es zoom in, si < 0 es zoom out
        '''
        if self.scene():
            if mode > 0:
                self.scene().request_zoom_in()
            elif mode < 0:
                self.scene().request_zoom_out()
        
        
    def mouseReleaseEvent(self, event):
        if event.buttons() & Qt.MidButton:
            self._mousePressPos = QPoint()
            event.accept()
        QGraphicsView.mouseReleaseEvent(self, event)
        
    def mouseMoveEvent(self, event):
        if self._mousePressPos.isNull():
            event.ignore()
            return
        
        if event.buttons() & Qt.MidButton:
            self.horizontalScrollBar().setValue(self._scrollBarValuesOnMousePress.x() - event.pos().x() + self._mousePressPos.x())
            self.verticalScrollBar().setValue(self._scrollBarValuesOnMousePress.y() - event.pos().y() + self._mousePressPos.y())
            self.horizontalScrollBar().update()
            self.verticalScrollBar().update()
            event.accept()
            
        QGraphicsView.mouseMoveEvent(self, event)

    
    def setScene(self, scene):
        #assert type(scene) == MultilayeredScene, "La escena %s no es una MultilayeredScene" % scene
        QObject.connect(scene, SIGNAL('scaleChange(float)'), self.do_scale)
        # No se propaga modo inicial a traves de la señal porque se setea en el
        # constructor.
        scene.set_view_mode(self.mode)
        QObject.connect(self, SIGNAL('modeChanged(int)'), scene.set_view_mode)
        QGraphicsView.setScene(self, scene)
    
    def do_scale(self, val):
        self.setMatrix(QMatrix().scale(val, val))
    
    
    def request_zoom_in(self):
        if self.scene():
            self.scene().request_zoom_in()
            
    def request_zoom_out(self):
        if self.scene():
            self.scene().request_zoom_out()
        
#------------------------------------------------------------------------------
# Capa
#------------------------------------------------------------------------------
class GraphicLayer(QGraphicsItemGroup):
    '''
    Capa, representa un nivel de zoom.
    '''
    FILE_INFO = re.compile('\-(?P<size>\d{2,5})_(?P<x0>\d{1,5})_(?P<y0>\d{1,5})\.\w{1,3}$')
    #INSTANCES = 0
    
    def __init__(self, dpi, dpi_info, dir_base, images):
        QGraphicsItemGroup.__init__(self)
        #GraphicLayer.INSTANCES += 1 
        self.dpi = dpi
        self.dpi_info = dpi_info
        self.dir_base = dir_base
        self.images = images
        self.setZValue(-10)
        self.__dimension = None
        self._relation = None
        
        # De esta manera se apilan las capas
        #self.setZValue(-100 + GraphicLayer.INSTANCES)
        #QObject.connect(self, SIGNAL('destroyed(QObject)'), GraphicLayer.restoreIndex)
        
    #@staticmethod
    #def restoreIndex(obj):
    #    GraphicLayer.INSTANCES -= 1
    
    def relation(): #@NoSelf
        doc = """Escala""" #@UnusedVariable
       
        def fget(self):
            return self._relation
           
        def fset(self, value):
            self._relation = value
            inv = 1 / float(value)
            self.scale(inv, inv)
            
        return locals()
       
    relation = property(**relation())
    
    
    def _get_dimensions(self):
        ''' Calcula las dimenciones de la capa en funcion al nombre de archivo '''
        if not self.__dimension:
            dims = map(lambda f: self.get_info(f), self.images)
            square_size = dims[0][0]
            max_x, max_y = max(map(lambda t: t[1], dims)), max(map(lambda t: t[2], dims))
            self.__dimension = max_x + square_size, max_y + square_size
        return self.__dimension
    
    dimensions = property(_get_dimensions, doc = "Dimenciones")
    
    def get_info(self, file):
        try:
            match = self.FILE_INFO.search(file)
            return map(lambda k: int(match.group(k)), ['size', 'x0', 'y0'])
        except AttributeError:
            print "No match de %s" % file
    
    def __str__(self):
        return "<%s DPI: %5d Cant slices: %3d Scale: %.4f %s W: %d H: %d>" % ( 
                self.__class__.__name__, self.dpi,
                len(self.images), self.relation or 0.0,
                self.isVisible() and "Visible" or "Oculto", 
                self.dimensions[0], self.dimensions[1])
    # Repr
    __repr__ = __str__
    
    def paint(self, painter, options, widget):
        QGraphicsItemGroup.paint(self, painter, options, widget)
        print "%s pintado a %.2f" % (self, painter.matrix().m11())
    
    
#===============================================================================
# Escena
#===============================================================================
class MultilayeredScene(QGraphicsScene):
    # Deprecado
    FOUR_POINTS = re.compile(r'\w*_(?P<x0>\d{1,5})_(?P<y0>\d{1,5})_(?P<x1>\d{1,5})_(?P<y1>\d{1,5}).jpg')
    
    DPI_X0_Y0 = re.compile(r'[\w\d_]+-(?P<dpi>\d{1,5})_(?P<x0>\d{1,5})_(?P<y0>\d{1,5}).jpg$')
    
    INITIAL_ZOOM = 1
    
    def __init__(self, parent = None):
        print "Construyendo escena"
        QGraphicsScene.__init__(self, 0, 0, 100, 100)
        self.layers = []    # Insntancias de Layer
        self._current_layer = None
        self._view_mode = MultilayeredViewer.View
        
    def set_view_mode(self, mode):
        self._view_mode = mode
    
    def clean(self):
        # Sacar las capas
        while self.layers:
            self.removeItem( self.layers.pop())
        
    def mode(self):
        pass
    
    def current_layer(): #@NoSelf
        doc = """Docstring""" #@UnusedVariable
       
        def fget(self):
            return self._current_layer
           
        def fset(self, value):
            assert isinstance(value, GraphicLayer)
            if value == self._current_layer:
                return
            self._current_layer = value
            map(lambda x: x.hide(), filter(lambda x: x is not value, self.layers))
            value.show()
            self.emit(SIGNAL('scaleChange(float)'), value.relation)
           
        return locals()
       
    current_layer = property(**current_layer())
    
    def current_layer_index(): #@NoSelf
        doc = """Docstring""" #@UnusedVariable
       
        def fget(self):
            return self.layers.index(self.current_layer)
           
        return locals()
       
    current_layer_index = property(**current_layer_index())
    
    def request_zoom_in(self):
        if self.current_layer_index < len(self.layers) - 1:
            self.current_layer = self.layers[self.current_layer_index + 1 ]
    
    def request_zoom_out(self):
        if self.current_layer_index > 0:
            self.current_layer = self.layers[self.current_layer_index -1 ]
    
    
    def loadFile(self, fname):
        # TODO: Quizas mejorar esta expresion
        dpi_re = re.compile('(?P<dpi>\d{2,4})')
        #self.t = QTimer(self)
        #self.connect(self.t, SIGNAL('timeout()'), self.processEvents)
        
        # Limpiamos el escenario
        self.clean()
        
        fname = str(fname)
        
        ftar = tarfile.open(fname, 'r')
        names = ftar.getnames()
        total = len(names)
        dirs = set(map(os.path.dirname, names))
        # Generamos la asociacion (dpi_x, sssss, dpi_x)
        map_layers = map(lambda x: (os.path.split(x)[-1], x) , dirs)
        tmp = []
        for dpi_info, dir_base in map_layers:
            # Rescatamos el número de DPIs desde el nombde interno de la carpeta
            dpi = int(dpi_re.search(dpi_info).group('dpi'))
            # Buscamos los nombres de archivo dentro
            images = filter(lambda x: x.startswith(dir_base), names)
            tmp.append( (dpi, dpi_info, dir_base, images) )
        # Ordenar por DPI
        tmp.sort(lambda x, y: cmp(x[0], y[0])) 
        # Carga ordenada de las imagenes
        cant =  0
        for dpi, dpi_info, dir_base, images in tmp:
            print "Carga de capa %d", dpi
            layer = GraphicLayer(dpi, dpi_info, dir_base, images)
            self.layers.append(layer)
            
            for image_name in images:
                f = ftar.extractfile( image_name )
                p = QPixmap()
                p.loadFromData( f.read() )
                # Usamos nuestro propio pixmap
                g = LayerPixmap(p)
                basename = os.path.basename(image_name)
                x0, y0 = self.get_info_fname(basename)
                g.setPos(x0, y0)
                layer.addToGroup( g )
                cant += 1   
                self.emit(SIGNAL('loadProgress(float)'), (cant / float(total)) * 100 )
                qApp.instance().processEvents()
            self.addItem(layer)
        
        
        # TODO: Esto es arbitrario, debería ser una en particular
        base_layer = self.layers[len(self.layers) / 2]
        self.setSceneRect(0,0, *base_layer.dimensions)
        self.set_base_layer(base_layer)
        self.current_layer = base_layer
            
    def set_base_layer(self, layer_1_1):
        ''' Establece las relaciones de escala '''
        print "Seteando layer 1:1 ", layer_1_1
        for l in self.layers:
            if l == layer_1_1:
                l.relation = 1
            else:
                l.relation = float(l.dpi) / layer_1_1.dpi
        
    def get_info_fname(self, fname):
        match = self.FOUR_POINTS.match(fname)
        if match:
            x0, y0, x1, y1 = map(lambda n: int(match.group(n)), ['x0', 'y0', 'x1', 'y1'])
            return x0, y0
        else:
            match = self.DPI_X0_Y0.match(fname)
            if match:
                dpi, x0, y0 = map(lambda n: int(match.group(n)), ['dpi', 'x0', 'y0'])
                return x0, y0
        
    def itemsOf(self, cls):
        ''' Una funcion para usar con el script de debug '''
        return filter(lambda i: isinstance(i, cls), self.items())

    def showItemsOf(self, cls, show = True):
        for item in self.itemsOf(cls):
            if show:
                item.show()
            else:
                item.hide()

class EditorMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Edicion de mapa')
        self.setWindowIcon(QIcon(':icons/res/layers.png'))
        self.setupActions()
        
        self.setupToolbars()
        self.setupMenus()
        self.setupCentralWidget()
        self.setupStatusBar()
        self.statusbar.showMessage('Editor de mapa inicializado.')
        QMetaObject.connectSlotsByName(self)
        
    def addTogglingAction(self, rootMenu, toolBar):
        action = rootMenu.addAction(toolBar.windowTitle())
        action.setCheckable(True)
        action.setChecked(not toolBar.isHidden())
        
        self.connect(action, SIGNAL('toggled(bool)'), toolBar.setShown)
        
        
    def setupActions(self):
        self.actionQuit = QAction(self.trUtf8("Salir"),self)
        self.actionQuit.setObjectName("actionQuit")
        self.actionQuit.setShortcut("Ctrl+Q")
        
        self.actionLoadTiles = QAction(u'Cargar', self)
        self.actionLoadTiles.setObjectName('actionLoadTiles')
        self.actionLoadTiles.setShortcut('Ctrl+O')
        self.actionLoadTiles.setIcon(QIcon(':icons/res/document-open-folder.png'))
        
        # Mano
        self.actionToolHand = QAction(u'Mano de arrastre', self)
        self.actionToolHand.setObjectName('actionToolHand')
        self.actionToolHand.setShortcut('Z')
        self.actionToolHand.setCheckable(True)
        self.actionToolHand.setStatusTip('Haga click y arrastre para desplazarse ene l lienzo')
        self.actionToolHand.setIcon(QIcon(':icons/res/transform-move.png'))
        
        #Lupa
        self.actionToolZoom = QAction(u'Lupa de zoom', self)
        self.actionToolZoom.setObjectName('actionToolZoom')
        self.actionToolZoom.setShortcut('X')
        self.actionToolZoom.setCheckable(True)
        self.actionToolZoom.setStatusTip('Click izquierod: Zoom In, Click Derecho: Zoom Out')
        self.actionToolZoom.setIcon(QIcon(':icons/res/xmag.png'))
        
        
        # Insertar Item
        self.actionToolDraw = QAction(u'Insertar Item', self)
        self.actionToolDraw.setObjectName('actionToolDraw')
        self.actionToolDraw.setCheckable(True)
        self.actionToolDraw.setShortcut('C')
        self.actionToolDraw.setIcon(QIcon(':icons/res/draw-freehand.png'))
        
        
        
        # Acction Group para las acciones "checkable" de edición
        # Exclusive actions
        self.actionGroupTools = QActionGroup(self)
        self.actionGroupTools.setExclusive(True)
        self.actionGroupTools.addAction(self.actionToolHand)
        self.actionGroupTools.addAction(self.actionToolZoom)
        self.actionGroupTools.addAction(self.actionToolDraw)
    
    
        
    def setupMenus(self):
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)
        self.menuFile = self.menubar.addMenu(self.trUtf8("&Archivo"))
        self.menuFile.addAction(self.actionLoadTiles)
        self.menuFile.addAction(self.actionQuit)
        
        self.menuView = self.menubar.addMenu(u'Vista')
        self.menuViewToolbars = self.menuView.addMenu('Barras de herramientas')
        
        self.addTogglingAction(self.menuViewToolbars, self.toolbarFile)
        self.addTogglingAction(self.menuViewToolbars, self.toolbarEdit)
        
        
        self.menuTool = self.menubar.addMenu(self.trUtf8('&Herramientas'))
        self.menuTool.addAction(self.actionToolHand)
        self.menuTool.addAction(self.actionToolZoom)
        
        
    def statusbarProgressLoading(self, amount):
        self.statusbar.showMessage('Cargado al %.2f%%' % amount)
    
        
    def setupCentralWidget(self):
        self.centralWidget = QWidget()
        layout = QVBoxLayout()
        self.centralWidget.setLayout(layout)
        self.setCentralWidget(self.centralWidget) 
        self.scene = MultilayeredScene()
        self.view = MultilayeredViewer()
        
        layout.addWidget(self.view)
        self.view.setScene(self.scene)
        
        self.connect(self.view, SIGNAL('zoomChanged(float)'), self.progressBarZoomNotify)
        self.connect(self.scene, SIGNAL('loadProgress(float)'), self.statusbarProgressLoading)
    
    def setupToolbars(self):
        
        self.toolbarFile = self.addToolBar('Archivo')
        self.toolbarFile.addAction(self.actionLoadTiles)
        
        self.toolbarEdit = self.addToolBar('Herramientas')
        self.toolbarEdit.addAction(self.actionToolHand)
        self.toolbarEdit.addAction(self.actionToolZoom)
        self.toolbarEdit.addAction(self.actionToolDraw)
        
        
    def progressBarZoomNotify(self, scale):
        self.statusbar.showMessage('Zoom: %d%%' % (scale * 100.0))
        
    def setupStatusBar(self):
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
    
    @pyqtSignature('')
    def on_actionQuit_triggered(self):
        self.hide()
    
    @pyqtSignature('')
    def on_actionLoadTiles_triggered(self):
        fname = QFileDialog.getOpenFileName(self, 'Cargar slices...', '', 
        'Mapas (*.map *.tar);; Todos los archivos (*)')
        if os.path.exists(fname):
            self.scene.loadFile(fname)
    
    @pyqtSignature('bool')
    def on_actionToolHand_toggled(self, checked):
        self.view.mode = checked and MultilayeredViewer.Hand or MultilayeredViewer.Normal

    @pyqtSignature('bool')
    def on_actionToolZoom_toggled(self, checked):
        self.view.mode = checked and MultilayeredViewer.Zoom or MultilayeredViewer.Normal
        
        
    @pyqtSignature('bool')
    def on_actionToolDraw_triggered(self, checked):
        self.view.mode = checked and MultilayeredViewer.Draw or MultilayeredViewer.Normal
    
try:
    import data_rc
    
#===============================================================================
# Código de preuba
#===============================================================================
except ImportError, e:
    sys.path.append('..')
    import data_rc #@UnusedImport

def main(argv = sys.argv):
    os.chdir('../../old/gveditor')
    app = QApplication(argv)
    win = EditorMainWindow()
    win.show()
    try:
        win.scene.loadFile('x_mapa_trelew.tar')
    except:
        pass
    print_matrix(QMatrix())
    app.exec_()
    

if __name__ == "__main__":
    if "__file__" in globals():
        path = os.path.dirname(__file__)
        if path:
            os.chdir(path)
    print "Comenzando con %d" % os.getpid()
    sys.exit(main())
