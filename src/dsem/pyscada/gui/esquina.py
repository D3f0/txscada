#! /usr/bin/env python
# -*- encoding: utf-8 -*-


from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from pyscada.gui.widgets import QComboBoxModelQuery
import math
import sys
from twisted.python import log

sys.path += ("..","../..")
from copy import copy

from picnet.bitfield import bitfield 

class GVAutoFitMixin(object):
    '''
    '''
    __autofit = False
    
    def autofit(): #@NoSelf
        doc = "Setea el autofit"
        def fget(self):
            return self.__autofit
        def fset(self, value):
            self.__autofit = value
            if value:
                self.__autoscale_bkp_matrix = self.matrix()
                self._autofit_scale()
            else:
                self.setMatrix(self.__autoscale_bkp_matrix)
                
        return locals()
    autofit = property(**autofit())
    
    def resizeEvent(self, event):
        if self.autofit:
            self._autofit_scale()
        QGraphicsView.resizeEvent(self, event)

    def _autofit_scale(self):
        # Obtenemos el QRectF de la escena y la del visor
        scene_rect, viewer_rect = self.scene().sceneRect(), self.rect()
        ratio_w = scene_rect.width() / viewer_rect.width()
        ratio_h = scene_rect.height() / viewer_rect.height()
        
        scale = 1.0 /(max (( ratio_w, ratio_h)))
        if scale < 1:
            # Un pequeño ajuste para que no se muestre la barra de scroll
            scale -= scale * (0.02)
        self.setMatrix(QMatrix().scale(scale, scale))

class EsquinaGraphicsView(QGraphicsView, GVAutoFitMixin):
    '''
    '''
    instance = None
    def __init__(self,scene, parent = None):
        '''
        Visualizador de la esquia
        '''
        QGraphicsView.__init__(self, parent)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setScene(scene)
        EsquinaGraphicsView.instance = self
        self.setRenderHint(QPainter.Antialiasing)
        self.face = 0 # Face 0 es la edicion de la esquina
        self.autofit = True
#        for i in self.items():
#            if type(i) == CalleGraphicsItem:
#                i.setAcceptHoverEvents(False)
        
#    def mousePressEvent(self, event):
#        # Do something according to the status
#        event.accept()
#
#    def mouseDoubleClickEvent(self, event):
#        event.accept()
#
#    def sceneEvent(self, event):
#        ''' Cuando el mouse entra en la figura '''
#        print ("entro al sceneEvent")
#        return False    
        
#
    
class EsquinaGraphicsScene(QGraphicsScene):
    '''
    Escena del mapa
    '''
    
    STATE_EDICION_CALLE = 0
    STATE_EDICION_SEMAFOROS = 1
    STATE_VISTA = 2  
    
    instance = None
    def __init__(self, x = None, y = None, width = None, height = None, parent = None):
        ''' Constructor '''
        QGraphicsScene.__init__(self)
        try:
            size = QRectF(x, y, width, height)
        except (ValueError, TypeError):
            size = QRectF(0,0,500, 500)
        self.setSceneRect(size)
        
        self.x = x
        self.y = y
        self.ancho = self.width()
        self.largo = self.height()
      
        brush = QBrush(QColor(0xaa,0xaa, 0xaa))
        self.setBackgroundBrush(brush)
    
        largoCalle = (self.height()/2)
        catetouno = self.width()/2
        catetodos = self.height()/2
        largoCalleDiagonal = math.sqrt(catetouno**2+catetodos**2)
        ancho = (self.width() * 0.20)
        self.calles = []
        
        
        widthSentro = (self.width()/2)
        heigthSentro = (self.height()/2)
        
        for i in range(8):
            if i%2 == 0: 
                self.calles.append(CalleGraphicsItem(ancho, largoCalle,angulo = 45*i))
            else:
                self.calles.append(CalleGraphicsItem(ancho, largoCalleDiagonal,angulo = 45*i))
                self.calles[i].tipo = CalleGraphicsItem.TIPO_CALLE_OUT
            self.calles[i].setPos(widthSentro,heigthSentro)
            self.addItem(self.calles[i])
        
        self.estado = self.STATE_EDICION_CALLE  

class SeleccionCalleDialog(QDialog):
    def __init__(self, inicial = None):
        QDialog.__init__(self)
        try:
            self.setWindowTitle(u"Selección de calle")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel('<h3>Seleccione una Calle</h3>'))
            self.comboCalles = QComboBoxModelQuery()
            
            layout.addWidget(self.comboCalles)
            self.update_model()
            
            self.buttonGroup = QDialogButtonBox(self)
            self.buttonGroup.setOrientation(Qt.Horizontal)
            self.buttonGroup.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
            self.connect(self.buttonGroup, SIGNAL("accepted()"), self.accept)
            self.connect(self.buttonGroup, SIGNAL("rejected()"), self.reject)
            
            layout.addWidget(self.buttonGroup)
            self.setLayout(layout)
        except Exception,e:
            print e
    
    def update_model(self):
        query = QSqlQuery('SELECT nombre, id FROM Calle ORDER BY nombre', qApp.instance().db_con)
        model = QSqlQueryModel(self.comboCalles)
        model.setQuery(query)
        self.comboCalles.setModel(model)
        self.comboCalles.setModelColumn(0)
    
    def exec_(self):
        return QDialog.exec_(self)
        
    def accept(self):
        self.id = self.comboCalles.get_col_value(1)
        self.nombre = self.comboCalles.currentText()
        QDialog.accept(self)
        
        
class CalleGraphicsItem(QGraphicsWidget):
    '''
    La clase QGraphicsItem es abstracta
    '''
     
    TIPO_AVENIDA = 0
    TIPO_DOBLEMANO = 1
    TIPO_CALLE_ENTRANTE = 2
    TIPO_CALLE_SALIENTE = 3
    TIPO_CALLE_OUT = 4 
    
    _shape = None 
    
    def __init__(self, ancho, largo, x = 0, y = 0, angulo = 0, tipo = 0,nombre = "",parent = None):
        QGraphicsWidget.__init__(self)
        self.setAcceptHoverEvents(True)
        
        self.ancho = ancho
        self.largo = largo
        self.posx = x
        self.posy = y
        
        # Indica si estamos usando la esquina llena
        self.tipo = tipo 
        
#        self.angulo = angulo
        #Le agrega en nombre a la calle         
        self.nombre = QString(nombre)
        
        self.semaforos = []
        self.angulo = 0
        self.anchoAvenida = ancho
        self.anchoCalleDoble = ancho*0.8
        self.anchoCalle = ancho*0.6
        
        self.rectAvenida = QRectF(0, -(self.anchoAvenida/2), self.largo, self.anchoAvenida)
        self.rectCalleDoble = QRectF(0, -(self.anchoCalleDoble/2), self.largo, self.anchoCalleDoble)
        self.rectCalle = QRectF(0, -(self.anchoCalle/2), self.largo, self.anchoCalle)
        # Cuando el mouse está encima del elemento
        self.hover = False
    
        self.menu = QMenu()
        self.actionCambiarNombre = self.menu.addAction('Cambiar Nombre')
        QObject.connect(self.actionCambiarNombre, SIGNAL('triggered()'), self.cambiarNombre)
        
        self.rotate(angulo)

    def _get_opacity(self):
        ''' Getter para la propiedad '''
        # guardar el valor de opacity de antes de modificarlo
        if self.tipo == 4:
            return self.hover and 0.50 or 0.0
        return 1
        
    opacity = property(_get_opacity, doc = "Nivel de transparencia")
    
    def _get_rect(self):
        ''' Getter para la propiedad '''
        if (self.tipo == self.TIPO_DOBLEMANO):
            return self.rectCalleDoble
        elif ((self.tipo == self.TIPO_CALLE_ENTRANTE) or (self.tipo == self.TIPO_CALLE_SALIENTE)):
            return self.rectCalle
        return self.rectAvenida
        
    rect = property(_get_rect, doc = "rect")    
    
    def _get_color(self):
        ''' Getter para la propiedad '''
        return self.hover and QColor(0xaf,0x11, 0xf2) or QColor(0xff,0xff, 0xff)    
    
    color = property(_get_color, doc = "Nivel de transparencia")
    
    def hoverEnterEvent(self, event):
        ''' Cuando el mouse entra en la figura '''
        if self.scene().estado == EsquinaGraphicsScene.STATE_EDICION_CALLE:
            self.hover = True
            self.setZValue(2)
            self.update()
    
    def hoverLeaveEvent(self, event):
        ''' Cuando el mouse sale de la figura '''
        self.hover = False
        self.setZValue(1)
        self.update()
        
    def shape(self):
        if not self._shape:
            self._shape = QPainterPath()
            self._shape.addRect(self.rect)
        return self._shape
    
    def rotate (self,angulo):
        self.angulo = (angulo + self.angulo) % 360 
        QGraphicsWidget.rotate(self, -angulo) 
        
    def paint(self, painter, option, widget):
        painter.setOpacity(self.opacity)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)
        flecha1 = QPolygonF([
                QPointF(0.0,-2.0),
                QPointF(10.0,-2.0),
                QPointF(10.0,-4.0),
                QPointF(15.0, 0.0),
                QPointF(10.0,4.0),
                QPointF(10.0,2.0),
                QPointF(0.0,2.0)
                ])
        flecha2 = QPolygonF([
                QPointF(0.0, 0.0),
                QPointF(5.0,-4.0),
                QPointF(5.0,-2.0),
                QPointF(15.0,-2.0),
                QPointF(15.0,2.0),
                QPointF(5.0,2.0),
                QPointF(5.0,4.0)
                ])
        painter.drawRect(self.rect)
        if self.tipo == 0:     
#           Dibija una Avenida
            painter.setPen(QColor(0,0,0))
            painter.drawRoundedRect((self.rect.width()*0.25), -((self.rect.height()*0.1)/2), self.rect.width()*0.75, (self.rect.height()*0.1),5,5)
            x0 = (self.rect.width()/2)
            y0 = (self.rect.height()/4)
            x1 = (self.rect.width()/2)
            y1 = -(self.rect.height()/4)
            flecha1.translate(x0,y0)
            flecha2.translate(x1,y1)
            painter.drawPolygon(flecha1);
            painter.drawPolygon(flecha2);
        elif self.tipo == 1:
#           Dibija una Calle doble mano 
            painter.setPen(QColor(0,0,0))
            x0 = (self.rect.width()/2)
            y0 = (self.rect.height()/4)
            x1 = (self.rect.width()/2)
            y1 = -(self.rect.height()/4)
            flecha1.translate(x0,y0)
            flecha2.translate(x1,y1)
            painter.drawPolygon(flecha1)
            painter.drawPolygon(flecha2)
        elif self.tipo == 2:
#           Dibija una Calle que sale del nodo 
            painter.setPen(QColor(0,0,0))
            x0 = (self.rectCalle.width()/2)
            y0 = 0
            flecha1.translate(x0,y0)
            painter.drawPolygon(flecha1);
        elif self.tipo == 3:
#           Dibija una Calle que entra al nodo 
            painter.setPen(QColor(0,0,0))
            x1 = (self.rectCalle.width()/2)
            y1 = 0
            flecha2.translate(x1,y1)
            painter.drawPolygon(flecha2)    
        painter.setPen(QColor(0,0,0))
        if self.angulo <= 90 or self.angulo >= 271:
            painter.drawText(self.rect, Qt.AlignRight|Qt.AlignHCenter ,self.nombre)
        else:
            painter.translate(self.rect.width(),0) 
            painter.rotate(180)
            painter.drawText(self.rect, Qt.AlignLeft ,self.nombre)
            
    def boundingRect(self):
        ''' Le pedimos a la figura correspondiente'''
        return self.rectAvenida   
        
    
    def  mousePressEvent(self, event):
        ''' Cuando se presiona sobre la figura, se cambia la propiedad llena 
        y se pide que se repinte'''
        if self.scene().estado != EsquinaGraphicsScene.STATE_VISTA:    
            if event.button() == 1:
                if self.scene().estado == EsquinaGraphicsScene.STATE_EDICION_CALLE:
                    self.tipo += 1
                    if self.tipo>4:
                        self.tipo=0
                    self.update()
                    qApp.emit(SIGNAL("modifiCalle"))
                if self.scene().estado == EsquinaGraphicsScene.STATE_EDICION_SEMAFOROS:
                    log.msg("Edicion semaforos, click derecho en la calle")
            elif event.button() == 2:
                if self.scene().estado == EsquinaGraphicsScene.STATE_EDICION_CALLE:
                    seleccionada = self.menu.exec_(event.screenPos())
                elif self.scene().estado == EsquinaGraphicsScene.STATE_EDICION_SEMAFOROS:
    #                seleccionada = self.menu2.exec_(event.screenPos())
                    log.msg("Edicion de semaforos")
                
                self.update()
        event.accept()
    
    
    def cambiarNombre(self):
        dialog = SeleccionCalleDialog(None)
        if dialog.exec_():
            self.nombre, self.id = dialog.nombre, dialog.id
        qApp.emit(SIGNAL("modifiCalle"))
        #texto,boolean = QInputDialog.getText(None,"","")
        #self.nombre = texto
              
    def insertar_semaforo(self,n_movi=-1, tipo = 0, x=None, y=None, uc=0, co=0, semaforo = None):
        sc = self.scene()
        if not x or not y:
            x = self.pos().x()
            y = self.pos().y()
        if semaforo:
            s = semaforo
            s.setPos(x,y)
            s.setCreador(self)
            s.co = co
            s.uc = uc
        else:
            s = Semaforo(n_movi,x,y,co=co,uc=uc,tipo = tipo )
        s.setAcceptDrops(True)
#        s.setPos(self.pos())
        s.setCreador(self)
        s.setMatrix(self.matrix())
        s.setZValue(4)
        s.scale(0.5,0.5)
        s.rotate(-90)
        sc.addItem(s)
        self.semaforos.append(s)
    
    def remover_semaforo(self, s):
        sc = self.scene()
        sc = sc.removeItem(s)
        self.semaforos.remove(s)
        s.setCreador(None)
        
          
class Semaforo(QGraphicsWidget):
    '''
    Clase para el semaforo.
    '''
    WIDTH, HEIGHT = 48, 136
    WIDTH_O, HEIGHT_O = 48, 100
    BASE_COLOR      = QColor(0x33, 0x4a, 0x4a)
    # On
    GREEN_COLOR_ON  = QColor.fromHsv(121, 230, 254)
    YELLOW_COLOR_ON = QColor.fromHsv(63, 226, 245)
    RED_COLOR_ON    = QColor.fromHsv(0, 226, 245)
    # Off
    GREEN_COLOR_OFF = QColor.fromHsv(121, 230, 64)
    YELLOW_COLOR_OFF= QColor.fromHsv(63, 226, 64)
    RED_COLOR_OFF   = QColor.fromHsv(0, 226, 48)
    
    BoundingRectComun = QRectF(0,0, WIDTH, HEIGHT)   
    BoundingRectOtro = QRectF(0,0, WIDTH_O, HEIGHT_O)   
    
    TIPO_COMUN = 0
    TIPO_PEATONAL = 3
    TIPO_DERECHA = 1
    TIPO_IZQUIERDA = 2
    
    # Este arreglo se indexa por los los bits 
    COLOR_BIT_MAPPING = {TIPO_COMUN:(
        (GREEN_COLOR_ON, YELLOW_COLOR_OFF, RED_COLOR_OFF, ), # 00
        (GREEN_COLOR_OFF, YELLOW_COLOR_OFF, RED_COLOR_ON, ), # 01 
        (GREEN_COLOR_OFF, YELLOW_COLOR_ON, RED_COLOR_OFF, ), # 10
        (GREEN_COLOR_OFF, YELLOW_COLOR_ON, RED_COLOR_ON, ),  # 11
        (GREEN_COLOR_OFF, YELLOW_COLOR_OFF, RED_COLOR_OFF, ),
        ),
        TIPO_DERECHA:(
        (GREEN_COLOR_ON, YELLOW_COLOR_OFF, RED_COLOR_OFF, ), # 00
        (GREEN_COLOR_OFF, YELLOW_COLOR_OFF, RED_COLOR_ON, ), # 01 
        (GREEN_COLOR_OFF, YELLOW_COLOR_ON, RED_COLOR_OFF, ), # 10
        (GREEN_COLOR_OFF, YELLOW_COLOR_ON, RED_COLOR_ON, ),  # 11
        (GREEN_COLOR_OFF, YELLOW_COLOR_OFF, RED_COLOR_OFF, ),
        ),
        TIPO_IZQUIERDA:(
        (GREEN_COLOR_ON, YELLOW_COLOR_OFF, RED_COLOR_OFF, ), # 00
        (GREEN_COLOR_OFF, YELLOW_COLOR_OFF, RED_COLOR_ON, ), # 01 
        (GREEN_COLOR_OFF, YELLOW_COLOR_ON, RED_COLOR_OFF, ), # 10
        (GREEN_COLOR_OFF, YELLOW_COLOR_ON, RED_COLOR_ON, ),  # 11
        (GREEN_COLOR_OFF, YELLOW_COLOR_OFF, RED_COLOR_OFF, ),
        ),
        TIPO_PEATONAL:(
        (GREEN_COLOR_ON, YELLOW_COLOR_OFF, RED_COLOR_OFF, ), # 00
        (GREEN_COLOR_OFF, YELLOW_COLOR_OFF, RED_COLOR_ON, ), # 01 
        (GREEN_COLOR_OFF, YELLOW_COLOR_ON, RED_COLOR_OFF, ), # 10
        (GREEN_COLOR_OFF, YELLOW_COLOR_ON, RED_COLOR_ON, ),  # 11
        (GREEN_COLOR_OFF, YELLOW_COLOR_OFF, RED_COLOR_OFF, ),
        ),
    }
        
    def __init__(self, n_movi=-1, x=0, y=0, tipo = 0, co = 0, uc = 0, parent = None):
        '''
        Constructor
        @param x: Posicion horizontal sobre la escena
        @param y: Posicion vertical sobre la escena
        '''
        
        QGraphicsWidget.__init__(self, parent)
        self.setPos(x, y)
        self.creador = parent
        
        self.tipo = tipo
        
        self.n_movi = n_movi
        
        self.setAcceptHoverEvents(True)
        
        #hace que el iten tenga drag and drop
        self.setFlag(QGraphicsItem.ItemIsMovable) 
        
        self.bit_update(4)
        
        #TODO: Ver si no está muy acoplado
        self.n_uc = 0
        self.n_port = 0
        self.n_bit = 0
        
        self.co = co
        self.uc = uc
        
        self.hover = False
        self.connect(qApp.instance(),SIGNAL("data_available"),self.actualizar)
    
    def actualizar(self,co,uc,svs,dis,ais,evs):
        ''' Actualizar '''
        if self.co == co and self.uc == uc:
            #1°b : 33 22 11 00
            #2°b : XX 66 55 44
            #3°b : XX 77 88 99
            #cga = bit 3 port 4
            print "entro a actualizar"
            movs = qApp.instance().cfg.movimientos
            if not bitfield(dis[movs.cga.port])[movs.cga.bit]:
                self.bit_update(4)
            else:
                log.msg(' '.join(map(lambda x: ('%x' % x).upper(), dis)))
                a,b = movs.pos[self.n_movi]
                l = copy(dis[0:3])
                l.reverse()
                bf = bitfield(l)
                self.bit_update(bf[a:b])
        pass
    def paint(self, painter, options, widget):
        ''' Dibuja el semáforo '''
        flecha = QPolygonF([
                    QPointF(-14.0,-4.0),
                    QPointF(5.0,-4.0),
                    QPointF(5.0,-8.0),
                    QPointF(14.0, 0.0),
                    QPointF(5.0,8.0),
                    QPointF(5.0,4.0),
                    QPointF(-14.0,4.0)
                    ])
            
        if self.tipo == self.TIPO_COMUN:
            painter.setPen(self.BASE_COLOR)
            painter.setBrush(QBrush(self.BASE_COLOR))
            # Dibujamos la figura de semáforo
            painter.drawPath(self.shape())
            
            painter.setPen(QColor(0xff, 0xff, 0xff))
            painter.setBrush(self.red)
            painter.drawEllipse(2,4,44,44)
            painter.setBrush(self.yellow)
            painter.drawEllipse(7,52,35,36)
            painter.setBrush(self.green)
            painter.drawEllipse(7,92,35,36)
        elif self.tipo == self.TIPO_DERECHA:
            painter.setPen(self.BASE_COLOR)
            painter.setBrush(QBrush(self.BASE_COLOR))
            # Dibujamos la figura de semáforo
            painter.drawPath(self.shape())
            
            painter.setPen(QColor(0xff, 0xff, 0xff))
            painter.setBrush(self.red)
            painter.drawEllipse(2,4,44,44)
            painter.setBrush(self.green)
            painter.drawEllipse(2,52,44,44)
            flecha.translate(24,26)
            painter.drawPolygon(flecha)    
            flecha.translate(0,48)
            painter.drawPolygon(flecha)    
         
        elif self.tipo == self.TIPO_IZQUIERDA:
            painter.setPen(self.BASE_COLOR)
            painter.setBrush(QBrush(self.BASE_COLOR))
            painter.drawPath(self.shape())     
            painter.setPen(QColor(0xff, 0xff, 0xff))
            painter.setBrush(self.red)
            painter.drawEllipse(2,4,44,44)
            painter.setBrush(self.green)
            painter.drawEllipse(2,52,44,44)
            flecha.translate(24,26)
            painter.translate(self.WIDTH_O, self.HEIGHT_O)
            painter.rotate(-180)
            painter.drawPolygon(flecha)    
            flecha.translate(0,48)
            painter.drawPolygon(flecha)
        elif self.tipo == self.TIPO_PEATONAL:
            painter.setPen(self.BASE_COLOR)
            painter.setBrush(QBrush(self.BASE_COLOR))
            # Dibujamos la figura de semáforo
            painter.drawPath(self.shape())
            
            painter.setPen(QColor(0xff, 0xff, 0xff))
            painter.setBrush(self.red)
            painter.drawEllipse(2,4,44,44)
            painter.setBrush(self.green)
            painter.drawEllipse(2,52,44,44)
    
    def boundingRect(self):
        ''' Retrona el area para el redibujado '''
        if self.tipo == self.TIPO_COMUN:
            return self.BoundingRectComun
        return self.BoundingRectOtro
        
    def shape(self):
        ''' Retorna la forma activa '''
        rectan = self.boundingRect()
        p = QPainterPath()
        p.addRoundedRect(rectan, 5.0,5.0)
        return p
    
    #def shape(self):
    def bit_update(self, bits):
        ''' Actualiza la GUI en funcion de los bits '''
        assert bits >= 0 and bits < 5, "Bits incorrectos"
        self.green, self.yellow, self.red = self.COLOR_BIT_MAPPING[self.tipo][bits] 
        self.update()
    
    def di_data_slot(self, n_uc, dis):
        #from twisted.python import log
        if n_uc == self.n_uc:
            #self.bit_update()
            port = bitfield(dis[self.n_port])
            
            bits = port[self.n_bit: self.n_bit +2] 
            self.bit_update(bits)
            #log.msg("Actualizando con %s" % bits)
    
    def mousePressEvent(self, event):
        event.accept()

    def hoverEnterEvent(self, event):
        ''' Cuando el mouse entra en la figura '''
        self.creador.hover = True
        self.creador.setZValue(2)
        self.creador.update()
        
        self.hover = True
        self.update()
        
    def hoverLeaveEvent(self, event):
        ''' Cuando el mouse sale de la figura '''
        self.hover = False
        self.creador.hover = False
        self.creador.setZValue(1)
        self.creador.update()
        self.update()     
    
    def setCreador(self,parent):
        self.creador = parent;

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setup_ui()
        self.setWindowTitle('Check de editor')
        
        QMetaObject.connectSlotsByName(self)
    
    def setup_ui(self):
        self.central_widget = QWidget(self)
        
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)
        layout.setMargin(2)
        layout.addWidget(QLabel("""<h3>Visualizador, editor de calles 
        y editor de semaforos </h3>
        """))
        combo = QComboBox(self)
        model = QStandardItemModel(3, 1,combo)
        model.setItem(0,0,QStandardItem(QString("Editar calles")))
        model.setItem(1,0,QStandardItem(QString("Editar semaforos")))
        model.setItem(2,0,QStandardItem(QString("Vista")))
        combo.setModel(model)
        combo.setCurrentIndex(0)
        combo.setObjectName('comboSelect')
        
        layout.addWidget(combo)
        
        # Setup the scene
        self.scene = EsquinaGraphicsScene(0,0,400,400)
#        items_rect = self.scene.sceneRect()
#        print "Putting items here", items_rect
#        for point in random_qpoints(items_rect, 10):
#            item = MyGraphicItem()
#            #items.append(item)
#            item.setPos(point)
#            self.scene.addItem(item)
#            print "Generando punto en", point
#            
        # Viewer Part
#        self.viewerGV = EsquinaGraphicsView(self.scene)
#        self.viewerGV.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding))
#        self.viewerGV.setScene( self.scene )
        
        
        # Editor Calle Part
        self.editorCGV = EsquinaGraphicsView(self.scene)
        
        # Editor Semaforo Part
#        self.editorSGV = EsquinaEditorSemaforosGraphicsView()
#        self.editorSGV.setScene( self.scene )
#        self.editorSGV.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding))
#        
        
        self.editorCGV.setBackgroundBrush(QBrush(QColor(0xFF, 0xEE, 0xAA)))
#        self.editorSGV.setBackgroundBrush(QBrush(QColor(0xFF, 0xEE, 0xAA)))
#        
        # Splitter
        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Horizontal)
#        self.splitter.addWidget( self.viewerGV )
        self.splitter.addWidget( self.editorCGV )
#        self.splitter.addWidget( self.editorSGV )
        
        # Puting everything together
        layout.addWidget(self.splitter)
        
        
        self.setCentralWidget(self.central_widget)
    
    @pyqtSignature("int")
    def on_comboSelect_currentIndexChanged(self, index):
        print "currentIndexChanged = %d"% index
        self.scene.estado = index
    
    @pyqtSignature("int")
    def on_comboSelect_highlighted(self, index):
        print "highlighted = %d"% index
    
def main(argv = sys.argv):
    '''
    Punto de entrada a la aplicacion.
    '''
    app = QApplication(argv)
    window = MainWindow()

    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
