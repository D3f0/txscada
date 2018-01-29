#! /usr/bin/env python
# -*- encoding: utf-8 -*-
__all__ = ('SimpleWizard', )

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from twisted.python import log
import sys
# Aumentanmos el path
sys.path += ('..', '../..')
from pyscada.gui.ui_wizard import Ui_WizardDialog



class ConfigWizard(QDialog, Ui_WizardDialog):
    '''
    Wizard de configuración
    '''
    _steps = []
    
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.history = []
        self.current_step = 0 # Es necesario ya que se defasa de len(history)
        self.setupUi(self)
        
        
    def steps(): #@NoSelf
        doc = """Pasos del wizard""" #@UnusedVariable
       
        def fget(self):
            return self._steps
           
        def fset(self, value):
            assert type(value) == list, "Los pasos deben ser una lista de clases"
            assert all(map(lambda x: issubclass(x, QWidget), value)), 'Cada paso del wizard debe extender de QWidget'
            self._steps = value
        return locals()
       
    steps = property(**steps())
        
        
    def on_pushBack_pressed(self):
        ''' El usuario pulsó el botón atrás '''
        old = self.history.pop()
        old.hide()
        self.layout().removeWidget(old)
        del old
        self.current_step -= 1
        widget = self.history[ self.current_step ]
        self.layout().insertWidget( 0, widget )
        widget.show()
        widget.setFocus()
        self.update_title()
        # Botones
        self.pushNext.setEnabled(True)
        self.pushFinish.setEnabled(False)
        self.pushBack.setEnabled( self.current_step >= 1)
        self.pushNext.setDefault(True)
        
        #self.pushCancel
    def on_pushNext_pressed(self):
        ''' El usuario pulsó el botón adelante '''
        old = self.history[ self.current_step ]
        old.hide()
        self.layout().removeWidget(old)
        
        
        self.current_step += 1
        
        self.pushBack.setEnabled(True)
        self.pushNext.setEnabled( self.current_step  < len(self.steps) )
        
        # Llegamos al útlimo paso?
        if self.current_step == len(self.steps) - 1:
            self.pushFinish.setEnabled( True )
            self.pushFinish.setDefault(True)
            self.pushNext.setEnabled(False)
        else:
            self.pushNext.setDefault(True)
            
        self.update_title()
        self.create_widget()
            
        
        
    def update_title(self):
        self.setWindowTitle('Paso %d de %d' % (
                                               self.current_step + 1,
                                               len(self.steps)
                                               ))
        
    def exec_(self):
        ''' Cuando se ejecuta el dialogo '''
        assert len(self.steps), "No se han definido pasos para el wizard"
        while self.history:
            x = self.history.pop()
            x.hide()
            del x
        # Desde el principio no se puede ir hacia atrás
        self.current_step = 0
        self.pushBack.setEnabled(False)
        self.pushFinish.setEnabled( len(self.steps) == 1)
        self.pushNext.setEnabled( len(self.steps) > 1)
        self.update_title()
        self.pushNext.setDefault(True)
        # Prueba
        self.create_widget()
        
        return QDialog.exec_(self)
    
    def create_widget(self):
        
        widget_class = self.steps[ self.current_step ] 
        widget = widget_class(self)
        
        self.history.append(widget)
        self.layout().insertWidget( 0, widget )
        widget.setFocus()
        return widget
        
    def removeWidget(self, widget):
        pass
    
    def accept(self):
        '''
        El diálogo es aceptado
        '''
        log.msg('Dialogo aceptado')
        QDialog.accept(self)
        
    def reject(self):
        '''
        El diálogo es rechazado.
        '''
        log.msg('Dialogo rechazado')
        QDialog.reject(self)

def main(argv = sys.argv):
    ''' Testing '''
    app = QApplication([])
    #wiz = CheckWizard()
    
    wiz = ConfigWizard()
    wiz.show()
    return app.exec_()
    
if __name__ == "__main__":
    sys.exit(main())

    