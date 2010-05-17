#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from esquina import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from twisted.python import log

class EsquinaView (QGraphicsView, GVAutoFitMixin):
    def __init__(self, scene, parent = None):
        '''
        Visualizador de la esquia
        '''
        QGraphicsView.__init__(self, parent)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.face = 0 # Face 0 es la edicion de la esquina
        self.autofit = True
        scene.estado = EsquinaGraphicsScene.STATE_VISTA
        
        
class EsquinaScene (EsquinaGraphicsScene):
    def __init__(self, x = None, y = None, width = None, height = None, parent = None, esquina_id = None):
        QGraphicsScene.__init__(self, parent)
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
        
        
            
        
        try:
            
            query_esquina = QSqlQuery("SELECT * FROM Esquina WHERE id = %d"% esquina_id)
            print "SELECT * FROM Esquina WHERE id = %d"% esquina_id
            if query_esquina.next():
                N_uc_id = query_esquina.record().indexOf('uc_id')
                uc_id = query_esquina.value(N_uc_id).toInt()[0]
            else:
                print "No se pudo obtener la esquina"
                return
            print "uc_id = %d"%uc_id
            
            query_uc = QSqlQuery("SELECT * FROM UC WHERE id = %d"% uc_id)
            print "SELECT * FROM UC WHERE id = %d"% uc_id
            if query_uc.next():
                N_co_id = query_uc.record().indexOf('co_id')
                N_id_UC = query_uc.record().indexOf('id_UC')
                co_id = query_uc.value(N_co_id).toInt()[0]
                id_UC = query_uc.value(N_id_UC).toInt()[0]
            else:
                print "No se pudo obtener la esquina"
                return
            print "co_id = %d"%co_id
            print "id_UC = %d"%id_UC
            
            
            
            
            
            #session = qApp.instance().SessionClass()
            query = QSqlQuery("SELECT * FROM Esquina_Calles WHERE esquina_id = %d"% esquina_id)
            print "SELECT * FROM Esquina_Calles WHERE esquina_id = %d"% esquina_id
            
            N_esquina_calle_id = query.record().indexOf('id')
            N_calle_id = query.record().indexOf('calle_id')
            N_angulo = query.record().indexOf('angulo')
            N_tipo_calle = query.record().indexOf('tipo_calle')
            
            while query.next():
                calle_id = query.value(N_calle_id).toInt()[0]
                query_calles = QSqlQuery("SELECT nombre FROM Calle WHERE id = %d"% calle_id)
                print "SELECT nombre FROM Calle WHERE id = %d"% calle_id
                if query_calles.next():
                    nombre = query_calles.value(0).toString()
                else:
                    print "no existe nombre de calle" 
                #TODO: ver si el angulo es entero o flotante
                angulo = query.value(N_angulo).toInt()[0]
                tipo_calle = query.value(N_tipo_calle).toInt()[0]
                calle_item = None
                if (angulo == 0) or (angulo%90 == 0):
                    calle_item = CalleGraphicsItem(ancho,largoCalle,nombre = nombre, angulo = angulo, tipo = tipo_calle, parent = parent)
                else:
                    calle_item = CalleGraphicsItem(ancho,largoCalleDiagonal,nombre = nombre, angulo = angulo, tipo = tipo_calle, parent = parent)
                self.calles.append(calle_item)
                
                esquina_calle_id = query.value(N_esquina_calle_id).toInt()[0]
                query_semaforos = QSqlQuery("SELECT * FROM Semaforo WHERE Esquina_Calles_id = %d"% esquina_calle_id)
                print "SELECT * FROM Semaforo WHERE Esquina_Calles_id = %d"% esquina_calle_id
                
                N_semaforos_ti_mov = query_semaforos.record().indexOf('ti_mov')
                N_semaforos_subti_mov = query_semaforos.record().indexOf('subti_mov')
                N_semaforos_n_mov = query_semaforos.record().indexOf('n_mov')
                N_semaforos_x = query_semaforos.record().indexOf('x')
                N_semaforos_y = query_semaforos.record().indexOf('y')
                
                calle_item.setPos(widthSentro,heigthSentro)
                self.addItem(calle_item)
                
                
                while query_semaforos.next():
                    # saco el tipo y subtipo de un linea de la db y armo el tipo
                    # de semaforo
                    ti_mov = query_semaforos.value(N_semaforos_ti_mov).toInt()[0]
                    subti_mov = query_semaforos.value(N_semaforos_subti_mov).toInt()[0]
 
                    if ti_mov:
                        tipo = Semaforo.TIPO_PEATONAL
                    else: 
                        tipo = subti_mov
                    
                    print "tipo de semaforo = %d"%tipo
                    #TODO: ver si x , y son enteros o flotantes
                    x = query_semaforos.value(N_semaforos_x).toInt()[0]
                    y = query_semaforos.value(N_semaforos_y).toInt()[0]
                    
                    n_mov = query_semaforos.value(N_semaforos_n_mov).toInt()[0]
                    
                    calle_item.insertar_semaforo(n_movi = n_mov,tipo = tipo, x=x, y=y, co = co_id, uc = id_UC)
                    print "Se inserto un semaforo a la calle"
                                                 
            if not query.lastError().type() == QSqlError.NoError: 
                print query.lastError().databaseText()
                    
        except Exception, e:
            print e, type(e)
            import traceback
            print traceback.format_exc()
            
        self.estado = self.STATE_EDICION_CALLE
        print "Termino de crearse la scene"
        
class Esquina_View_Dialog(QWidget):
    def __init__(self,parent, esquina_id):
        QWidget.__init__(self,parent)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle('Visualizador de tiempo real')
        self.scene = EsquinaScene(0,0,500,500, parent = self, esquina_id = esquina_id)
        self.view = EsquinaView(self.scene)
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)
        self.show()
        # TODO: Poner el poll exlcusivo de la UC
        
    def closeEvent(self,event):
        for c in self.scene.calles:
            for s in c.semaforos:
                # La desconexión la realizamos contra la misma signatura de la conexión
                # ya que sospechamos que sea una conexión a nivel sip/Python y no 
                # una en el ambiente C++.
                #   self.connect(qApp.instance(),SIGNAL("data_available"),self.actualizar)
                ok = s.disconnect(qApp.instance(), SIGNAL("data_available"), s.actualizar)
                log.msg('Desconexion semaforo: %s' % ok)
        QWidget.closeEvent(self,event)
        # Notificar hacia arriba
        self.emit(SIGNAL("close"))
        # TODO: Quitar el poll exclusivo de la UC
        
    
        

if __name__ == '__main__':
    from qt_dbhelp import dburl_to_qsqldb
    app = QApplication([])
    app.db_con = dburl_to_qsqldb('mysql://dsem:passmenot@localhost:3306/dsem')
    d = Esquina_View_Dialog(app, 18)
    d.show()
    app.exec_()