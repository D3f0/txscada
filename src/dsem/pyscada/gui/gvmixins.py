#! /usr/bin/env python
# -*- encoding: utf-8 -*-

__all__ = ('GVAutoFitMixin', )

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport

class GVAutoFitMixin(object):
    '''
    Mixin para utofit de una una GraphicsView en su escena.
    '''
    __autofit = False
    __autoscale_bkp_matrix = QMatrix()
    
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
        if not self.scene():
            return
        
        # Obtenemos el QRectF de la escena y la del visor
        scene_rect, viewer_rect = self.scene().sceneRect(), self.rect()
        try:
            ratio_w = scene_rect.width() / viewer_rect.width()
            ratio_h = scene_rect.height() / viewer_rect.height()
        except ZeroDivisionError, e:
            pass
        else:
        
            scale = 1.0 /(max (( ratio_w, ratio_h)))
            if scale < 1:
                # Un pequeño ajuste para que no se muestre la barra de scroll
                scale -= scale * (0.02)
            self.setMatrix(QMatrix().scale(scale, scale))


class GVZoomingScrollingMixin(object):
    '''
    Rejunte de códgio de varios de los ejemplos de Qt.
    Algunos de QScrollArea
    '''
    MOVE_BUTTONS = Qt.MidButton
    MAX_ZOOM = 2
    MIN_ZOOM = 0.2
    ZOOM_STEP = 0.1
    INITIAL_ZOOM = 1
    # Some needed attributes 
    _current_zoom = INITIAL_ZOOM
    _mousePressPos = QPoint()
    _scrollBarValuesOnMousePress = QPoint()

# Un MIXIN no tiene INIT    
#    def __init__(self, parent = None):
#        QGraphicsView.__init__(self, parent)
#        self.current_zoom = self.INITIAL_ZOOM
#        self._mousePressPos = QPoint()
#        self._scrollBarValuesOnMousePress = QPoint()
#        self.setRenderHint(QPainter.NonCosmeticDefaultPen)
        
    def wheelEvent(self, event):
        numDegrees = event.delta() / 8
        numSteps = numDegrees / 15

        if event.orientation() == Qt.Vertical:
            self.zoom(numSteps)
        
        event.accept();
        
    def zoom(self, steps):
        
        if steps > 0:
            if self._current_zoom < self.MAX_ZOOM:
                self._current_zoom += self.ZOOM_STEP
        else:
            if self._current_zoom > self.MIN_ZOOM:
                self._current_zoom -= self.ZOOM_STEP

        matriz = QMatrix()
        matriz.scale(self._current_zoom, self._current_zoom)
        self.setMatrix(matriz)
        self.update()
    
    def mousePressEvent(self, event):
        if event.buttons() & self.MOVE_BUTTONS:
            self._mousePressPos = QPoint(event.pos())
            self._scrollBarValuesOnMousePress.setX(self.horizontalScrollBar().value())
            self._scrollBarValuesOnMousePress.setY(self.verticalScrollBar().value())
        
        #QGraphicsView.mousePressEvent(self, event)
        
    def mouseReleaseEvent(self, event):
        if event.buttons() & self.MOVE_BUTTONS:
            self._mousePressPos = QPoint()
            event.accept()
        #QGraphicsView.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        if self._mousePressPos.isNull():
            event.ignore()
            return
        
        if event.buttons() & self.MOVE_BUTTONS:
            self.horizontalScrollBar().setValue(self._scrollBarValuesOnMousePress.x() - event.pos().x() + self._mousePressPos.x())
            self.verticalScrollBar().setValue(self._scrollBarValuesOnMousePress.y() - event.pos().y() + self._mousePressPos.y())
            self.horizontalScrollBar().update()
            self.verticalScrollBar().update()
            event.accept()
        #QGraphicsView.mouseMoveEvent(self, event)