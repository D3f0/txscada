#! /usr/bin/env python
# -*- encoding: utf-8 -*-


from PyQt4.Qt import *
#from PyQt4.QtCore import *
from zooming import ZoomingScrollingGraphicsView as ZoomGraphicsView
from pyscada.gui.esquina_view_dialog import Esquina_View_Dialog

class MapView(ZoomGraphicsView):
    '''
    '''
    MAX_ZOOM = 5
    instance = None
    def __init__(self, parent = None):
        '''
        Visualizador de mapa
        '''
        #QGraphicsView.__init__(self, parent)
        ZoomGraphicsView.__init__(self, parent)
        self.scene = MapScene()
        self.setScene(self.scene)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        MapView.instance = self
        self.setRenderHint(QPainter.Antialiasing)
        
    def mouseMoveEvent(self, event):
        ZoomGraphicsView.mouseMoveEvent(self, event)
        p = event.pos()
        #qApp.instance().win.statusbar.showMessage('Posicion %s %s' % (p.x(), p.y()))
        
        
        
    def mousePressEvent(self, event):
        # Padre
        #print event
        ZoomGraphicsView.mousePressEvent(self, event)
        item = self.itemAt(event.pos())
        if item and event.buttons() & Qt.LeftButton:
            item.color = QColor(255,23,23)
            item.update()
            #QMessageBox.information(None, "Item", "Item %s" % item)
#        
#        #self.scene.mousePressEvent(event)
#        
#        #qApp.instance().win.statusbar.showMessage('X: %.5f Y: %.5f' % (pos.x(), pos.y())        

        
class MapScene(QGraphicsScene):
    '''
    Escena del mapa
    '''
    WIDTH = 1000
    HEIGHT = 1000
    
    instance = None
    def __init__(self):
        ''' Constructor '''
        QGraphicsScene.__init__(self, 0, 0, MapScene.WIDTH, MapScene.HEIGHT)
        self.addText('Mapa de la ciudad de Trelew')
        MapScene.instance = self
        
    def mouseDoubleClickEvent(self, event):
        ''' Evento de doble click '''
        if event.buttons() & Qt.LeftButton:
            pos =  event.scenePos()
            if not self.itemAt(pos):
                self.addItem(TestiItem(pos.x(), pos.y()))
        
    def _mousePressEvent(self, event):
        QMessageBox.information(None, 'Evento', '%s' % event)
            
class TestiItem(QGraphicsItem):
    
    def __init__(self, x, y):
        self.animation = None
        QGraphicsItem.__init__(self)
        self.setPos(x, y)
        self.color = QColor(0x2e,0xbd, 0xaf)
        self.rect = (-5, -5, 10, 10)
        
        self.timer = QTimer(None)
        self.factor = 1
        self.final_factor = 2
        self.increment = 0.1
        
        QObject.connect(self.timer, SIGNAL('timeout()'), self.convulse)
        self.timer.start(1000/33)
        
        # Menu
        self.menu = QMenu()
        self.actionAnimar = self.menu.addAction('Animar')
        self.actionDetner = self.menu.addAction('Detner')
        self.actionEliminar = self.menu.addAction('Eliminar')
        QObject.connect(self.actionEliminar, SIGNAL('triggered()'), self.eliminar)
        QObject.connect(self.actionAnimar, SIGNAL('triggered()'), self.animar)
        QObject.connect(self.actionDetner, SIGNAL('triggered()'), self.detener)
    def animar(self):
        self.animation = BreatheAnimation(self, repeat = True)
        self.animation.start()
        
    def detener(self):
        pass
        
    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(*self.rect)
    
    def eliminar(self):
        MapScene.instance.removeItem(self)
    
    def convulse(self):
        '''
        Esto tendríamos que ponerlo en otra clase para que no ensucie.
        El QGraphicsItemAnimation parece que puede ayudar a este proósito.
        '''
        if self.factor < self.final_factor:
            self.factor += self.increment
        else:
            self.timer.stop()
        self.setMatrix(QMatrix().scale(self.factor, self.factor))
        
    def contextMenuEvent(self, event):
        '''
        Solo de pruebas
        '''
        seleccionada = self.menu.exec_(event.screenPos())
#        if seleccionada:
#            QMessageBox.information(None, "Seleccion", "Selecionaste %s" % seleccionada)
        
    
    
#    def shape(self):
#        pass
    def __str__(self):
        return "GraphcsItem"
    
    def boundingRect(self):
        return QRectF(-5,-5,10,10)

class BreatheAnimation(QGraphicsItemAnimation):
    def __init__(self, item, repeat = False, autostart = False):
        QGraphicsItemAnimation.__init__(self)
        self.timer = QTimeLine(2000)
        self.timer.setFrameRange(0, 100)
        if item:
            self.setItem(item)
        self.setTimeLine(self.timer)
        
        scale = [ x /100.0 for x in range(100,400, (400-100)/100) ] + \
                [ x /100.0 for x in range(400,100, -((400-100)/100)) ]
        
        for i in range(1,200):
            #self.setPosAt(i / 200.0, QPointF(i,i))
            self.setScaleAt(i /200.0, scale[i], scale[i])
            
        if repeat:
            self.connect(self.timer, SIGNAL('finished()'), self.timer, SLOT('start()'))
            
        if autostart:
            self.start()
        
    def start(self):
        self.timer.start()
        
