#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt4 import QtCore, QtGui, QtSvg
from os.path import join, sep
import random


class MapItem(QtSvg.QGraphicsSvgItem):
    def __init__(self):
        QtSvg.QGraphicsSvgItem.__init__(self, 'res/map/beta.svg')
        self.setMatrix(QtGui.QMatrix().scale(3.4,3.4))


class MapScene(QtGui.QGraphicsScene):
    def __init__(self, parent = None):
        base_path = QtGui.QApplication.instance().path
        QtGui.QGraphicsScene.__init__(self, 0, 0, 1000.0, 1000.0, parent)
        #self.setBackgroundBrush(join(base_path, 'res%sback.png' % sep))
        
        
        #self.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/icons/res/back.png')))
        
#        for i in range(100):
#            x, y, x1, y1 = [ random.randint(100,999) for x in range(4) ]
#            self.addRect(x,y,x1,y1)
        
        #self.map_item = MapItem()
           
        self.addPixmap(QtGui.QPixmap('res/map/mapa.png'))