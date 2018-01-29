#! /usr/bin/env python
# -*- encoding: utf-8 -*-

__all__ = ('BooleanDelegate', 
           'IntegerRangeDelegate', 
           'FloatRangeDelegate',
           'IPAddressTextDelegate',
           'ComboBoxDelegate',
#           'CalleComboBoxDelegate',
#           'TipoSemaforoDelegate',
           'NullDelegate',
           'ComboBoxListDelegate',
           'IPAddressLooseDelegate',
           )

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from twisted.python import log

class BooleanDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        
        editor = QComboBox(parent)
        editor.addItem('Habilitado', QVariant(1))
        editor.addItem('Deshabilitado', QVariant(0))
        return editor
        
    def setEditorData(self, editor, index):
        data = index.model().data(index, Qt.DisplayRole)
        editor.setCurrentIndex( editor.findData(data) )
    
    def setModelData(self, editor, model, index):
        val = editor.itemData( editor.currentIndex() )
        model.setData(index, val)
        #if type(model) == QSqlTableModel:
        #    model.submitAll()
    
    
class IntegerRangeDelegate(QItemDelegate):
    def __init__(self, min, max, step, parent = None):
        QItemDelegate.__init__(self, parent)
        self.min = min
        self.max = max
        self.step = step
        
    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setMinimum(self.min)
        editor.setMaximum(self.max)
        editor.setSingleStep(self.step)
        return editor
    
    def setEditorData(self, editor, index):
        try:
            data = index.model().data( index, Qt.DisplayRole).toInt()[0] 
        except IndexError:
            data = self.min
        editor.setValue ( data )
        
    def setModelData(self, editor, model, index):
        val = QVariant( editor.value() )
        model.setData( index, val)
        if type(model) == QSqlTableModel:
            model.submitAll()

class FloatRangeDelegate(QItemDelegate):
    def __init__(self, min, max, step, parent = None):
        QItemDelegate.__init__(self, parent)
        self.min = min
        self.max = max
        self.step = step
        
    def createEditor(self, parent, option, index):
        
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(self.min)
        editor.setMaximum(self.max)
        editor.setSingleStep(self.step)
        return editor
    
    def setEditorData(self, editor, index):
        try:
            data = index.model().data( index, Qt.DisplayRole).toDouble()[0]
        except IndexError:
            data = self.min
        editor.setValue( data )
        
    def setModelData(self, editor, model, index):
        val = QVariant( editor.value() )
        model.setData( index, val)
        if type(model) == QSqlTableModel:
            model.submitAll()

class IPAddressTextDelegate(QItemDelegate):
    def __init__(self, default = '127.0.0.1', parent = None):
        QItemDelegate.__init__(self, parent)
        self.default = default
        
    def createEditor(self, parent, option, index):
        editor = QLineEdit(self.default, parent)
        editor.regexp = QRegExp('(\d{1,3}\.){4}')
        editor._validator = QRegExpValidator(editor.regexp, editor)
        editor.setValidator(editor._validator)
        return editor
    
class IPAddressLooseDelegate(QItemDelegate):
    FORBBIDEN_IPS = (
                     (0,0,0,0),
                     (255,255,255,255),
                     (1,1,1,1),
                     )
    
    def __init__(self, model, default = '127.0.0.1', parent = None):
        QItemDelegate.__init__(self, parent)
        self.model = model
        self.default = default
    
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        try:
            data = self.model.data(index).toString()
            if data:
                editor.setText(data)
            else:
                editor.setText(self.default)
        except:
            pass
        #editor.setMaximumSize()
        return editor
    
    def setModelData(self, editor, model, index):
        #original_data = model.data(index)
        text = editor.text()
        try:
            ints = tuple(map(int, text.split('.')))
            assert len(ints) == 4, "No son cuatro enteros"
            assert all( map( lambda i: i>=0 and i <= 255, ints)), "Valores invalidos"
            assert ints not in self.FORBBIDEN_IPS, "IP prohibida"
        except Exception, e:
            # No es una IP válida
            log.err(e)
            pass
        else:
            model.setData( index, QVariant(text) )
            #if type(model) == QSqlTableModel:
            #    model.submitAll()
        
        
        
            
    
class ComboBoxDelegate(QItemDelegate):
    def __init__(self, nombre_ids, parent = None):
        QItemDelegate.__init__(self, parent)
        self.nombre_ids = nombre_ids
    
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItem('', QVariant(-1))
        for n,id in self.nombre_ids:
            editor.addItem(n, QVariant(id))
        return editor
        
    def setEditorData(self, editor, index):
        data = index.model().data(index, Qt.DisplayRole)
        editor.setCurrentIndex( editor.findData(data) )
    
    def setModelData(self, editor, model, index):
        id = editor.itemData( editor.currentIndex() )
        val = editor.currentText()
        model.setData(index, QVariant(val))
        model.setData(model.index(index.row(),index.column()+1), id)
        # Para que funcione el movimiento de zape
        if type(model) == QSqlTableModel:
            model.submitAll()
  
class NullDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        return
    
class ComboBoxListDelegate(QItemDelegate):
    def __init__(self, nombre_ids, callback_condicion,parent = None):
        QItemDelegate.__init__(self, parent)
        self.nombre_ids = nombre_ids
        self.condicion = callback_condicion
    
    def createEditor(self, parent, option, index):
        if self.condicion(index):
            editor = QComboBox(parent)
            editor.addItem('', QVariant())
            for n,id in self.nombre_ids:
                editor.addItem(n, QVariant(id))
            self.connect(editor, SIGNAL('highlighted(int)'), self.iluminacion)
            return editor
        
    def setEditorData(self, editor, index):
        data = index.model().data(index, Qt.DisplayRole)
        editor.setCurrentIndex( editor.findData(data) )
    
    def setModelData(self, editor, model, index):
        id = editor.itemData( editor.currentIndex() )
        val = editor.currentText()
        model.setData(index, QVariant(val))
        model.setData(model.index(index.row(),index.column()+1), id)
        if type(model) == QSqlTableModel:
            model.submitAll()
        self.emit(SIGNAL("changeModelData"),id,index)
    
    #@pyqtSignature("int")   
    def iluminacion(self,index):
        self.emit(SIGNAL("iluminacionCombobox"),index)