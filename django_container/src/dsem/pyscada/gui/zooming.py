#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ZoomingScrollingGraphicsView(QGraphicsView):
    '''
    Rejunte de códgio de varios de los ejemplos de Qt.
    Algunos de QScrollArea
    '''
    MOVE_BUTTONS = Qt.MidButton
    MAX_ZOOM = 2
    MIN_ZOOM = 0.2
    ZOOM_STEP = 0.1
    INITIAL_ZOOM = 1
    
    def __init__(self, parent = None):
        QGraphicsView.__init__(self, parent)
        self.current_zoom = self.INITIAL_ZOOM
        self._mousePressPos = QPoint()
        self._scrollBarValuesOnMousePress = QPoint()
        self.setRenderHint(QPainter.NonCosmeticDefaultPen)
        
    def wheelEvent(self, event):
        numDegrees = event.delta() / 8
        numSteps = numDegrees / 15

        if event.orientation() == Qt.Vertical:
            self.zoom(numSteps)
        
        event.accept();
        
    def zoom(self, steps):
        
        if steps > 0:
            if self.current_zoom < self.MAX_ZOOM:
                self.current_zoom += self.ZOOM_STEP
        else:
            if self.current_zoom > self.MIN_ZOOM:
                self.current_zoom -= self.ZOOM_STEP

        matriz = QMatrix()
        matriz.scale(self.current_zoom, self.current_zoom)
        self.setMatrix(matriz)
        self.update()
    
    def mousePressEvent(self, event):
        if event.buttons() & self.MOVE_BUTTONS:
            self._mousePressPos = QPoint(event.pos())
            self._scrollBarValuesOnMousePress.setX(self.horizontalScrollBar().value())
            self._scrollBarValuesOnMousePress.setY(self.verticalScrollBar().value())
        
        QGraphicsView.mousePressEvent(self, event)
        
    def mouseReleaseEvent(self, event):
        if event.buttons() & self.MOVE_BUTTONS:
            self._mousePressPos = QPoint()
            event.accept()
        QGraphicsView.mouseReleaseEvent(self, event)

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
        QGraphicsView.mouseMoveEvent(self, event)

    