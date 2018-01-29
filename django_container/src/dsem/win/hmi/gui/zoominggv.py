#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from PyQt4 import QtGui, QtCore

class ZoomingScrollingGraphicsView(QtGui.QGraphicsView):
    MAX_ZOOM = 10
    MIN_ZOOM = 0.2
    ZOOM_STEP = 0.1
    INITIAL_ZOOM = 1
    
    def __init__(self, parent = None):
        QtGui.QGraphicsView.__init__(self, parent)
        self.current_zoom = self.INITIAL_ZOOM
        self._mousePressPos = QtCore.QPoint()
        self._scrollBarValuesOnMousePress = QtCore.QPoint()
        #self.setRenderHint(QtGui.QPainter.NonCosmeticDefaultPen)
        
    def wheelEvent(self, event):
        numDegrees = event.delta() / 8
        numSteps = numDegrees / 15

        if event.orientation() == QtCore.Qt.Vertical:
            self.zoom(numSteps)
        
        event.accept();
        
    def zoom(self, steps):
        
        if steps > 0:
            if self.current_zoom < self.MAX_ZOOM:
                self.current_zoom += self.ZOOM_STEP
        else:
            if self.current_zoom > self.MIN_ZOOM:
                self.current_zoom -= self.ZOOM_STEP

        matriz = QtGui.QMatrix()
        matriz.scale(self.current_zoom, self.current_zoom)
        self.setMatrix(matriz)
        self.update()
    
    def mousePressEvent(self, event):
        self._mousePressPos = QtCore.QPoint(event.pos())
        self._scrollBarValuesOnMousePress.setX(self.horizontalScrollBar().value())
        self._scrollBarValuesOnMousePress.setY(self.verticalScrollBar().value())
        event.accept()

    def mouseMoveEvent(self, event):
        if self._mousePressPos.isNull():
            event.ignore()
            return

        self.horizontalScrollBar().setValue(self._scrollBarValuesOnMousePress.x() - event.pos().x() + self._mousePressPos.x())
        self.verticalScrollBar().setValue(self._scrollBarValuesOnMousePress.y() - event.pos().y() + self._mousePressPos.y())
        self.horizontalScrollBar().update()
        self.verticalScrollBar().update()
        event.accept()

    def mouseReleaseEvent(self, event):
        self._mousePressPos = QtCore.QPoint()
        event.accept()


