#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from delegates import *
import os, sys
from sqlalchemy import create_engine
from pyscada.model import metadata
from twisted.python import log

try:
    from pyscada.gui.wizard import ConfigWizard
    from pyscada.gui.widgets import QComboBoxModelQuery
    
except ImportError:
    sys.path += ('..', '..%s..' % os.sep)
    from pyscada.gui.wizard import ConfigWizard 

from esquina import *



class EsquinaConfigWizard(ConfigWizard):
    '''
    Wizard de configuracion de la esquina.
    '''
    esquina_id = -1
    def __init__(self, parent):
        ConfigWizard.__init__(self)
        self.item = parent
        self.inicializacion_fallo = False
        
        self.steps = [  SeleccionCOyUC,
                        ConfiguracionCalles,
                        ConfiguracionSemaforos,
                      ]
        
        try:
            self.create_widget()
        except Exception, e:
            # Marcamos el fallo
            self.inicializacion_fallo = True
            QMessageBox.critical(None, "Error", "%s" % e)
            
    def exec_(self):
        # Prevenir la ejecución del wizard si fallo la inicializacion del primer wizard
        if not self.inicializacion_fallo:
            return ConfigWizard.exec_(self)
    
    def accept(self):
        '''
        Accept de el dialogo.
        Esto crea el punto en la DB y las instancias de Esquina_Calle 
        correspondientes.
        '''
        
        query = QSqlQuery()
        # Ejecutar un START TRANSACTION sobre Qt 4.5 parece generar
        # error de segmentación.
        #query.exec_("START TRANSACTION")
        
        uc_id = self.history[0].comboUCs.get_col_value(1)
        transaction = qApp.instance().db_con.transaction()
        log.msg('Inicio de la tranasccion? %s' % transaction)
        
        try:
            
            x, y = self.item.pos().x(), self.item.pos().y()
            
            query.exec_("INSERT INTO Esquina (uc_id, x, y) VALUES (%d, %d, %d)" \
                        % (uc_id, x, y))
            
            esquina_id = query.lastInsertId().toInt()[0]
            self.calles = []
            for calle in self.history[1].scene.calles:
                if calle.tipo != CalleGraphicsItem.TIPO_CALLE_OUT:
                    log.msg('DEBUG: %s' % str((esquina_id,
                                           calle.id,
                                           int(calle.angulo),
                                           calle.tipo)))
                    query.exec_("""
                        INSERT INTO Esquina_Calles (esquina_id, calle_id, angulo,
                                                    tipo_calle) VALUES 
                                                    (%d, %d, %d, %d)""" %
                                                    (esquina_id,
                                                     calle.id,
                                                     int(calle.angulo),
                                                     calle.tipo))
                    esquina_calles_id = query.lastInsertId().toInt()[0]
                    for semaforo_item in calle.semaforos:
                        pos = semaforo_item.pos()
                        
                        query.exec_( """UPDATE Semaforo SET Esquina_Calles_id = %d,
                                                ti_mov = %d, subti_mov = %d, x = %d, y = %d
                                                WHERE uc_id = %d AND n_mov = %d
                                    """ % (esquina_calles_id,
                                           semaforo_item.tipo == Semaforo.TIPO_PEATONAL and 1 or 0,
                                           semaforo_item.tipo < 3 and semaforo_item.tipo or 0,
                                           pos.x(), pos.y(), uc_id, semaforo_item.n_movi
                                           ))         
#                        
                        log.msg( """ Semaforo (uc_id=%d, esquina_calles_id=%d,ti_mov=%d,subti_mov=%d,
                                n_movi=%d, x=%d, y=%d)"""%(uc_id, 
                               esquina_calles_id, 
                               semaforo_item.tipo == Semaforo.TIPO_PEATONAL and 1 or 0,
                               semaforo_item.tipo < 3 and semaforo_item.tipo or 0,
                               semaforo_item.n_movi, pos.x(), pos.y() 
                        ))
            
            if not query.lastError().type() == QSqlError.NoError:
                if transaction:
                    qApp.instance().db_con.rollback()
                log.err('Error en la DB: %s' % query.lastError().databaseText())
            else:
                if transaction:
                    commit = qApp.instance().db_con.commit()
                    log.msg('Commit exitoso %s' % commit)
                self.esquina_id = esquina_id
            
        except Exception, e:
            log.err(str(e))
            if transaction:
                qApp.instance().db_con.rollback()
        return ConfigWizard.accept(self)
    
class SeleccionCOyUC(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
        layout = QVBoxLayout(self)
        label1 = QLabel('''
        <h3>Seleccione el concentrador y la UC</h3>
        <p>Seleccione un concentrador de la lista inferior</p>
        ''', self)
        layout.addWidget(label1)
        self.comboCOs = QComboBoxModelQuery(self)
        self.comboCOs.setObjectName('comboCOs')
        
        query = QSqlQuery('''
            SELECT 
                CONCAT(COALESCE(CO.nombre_co, 'CO'), ' ' ,COALESCE(CO.ip_address, 'Sin IP')) `nombre`,
            id_CO FROM CO''')
        if not query.size():
            log.msg("No existen concentradores")
            raise Exception('No existen concentradores')
        
        
        log.err("Error: %s" % query.lastError().databaseText())
        model = QSqlQueryModel(self.comboCOs)
        model.setQuery(query)
        self.comboCOs.setModel(model)
        layout.addWidget(self.comboCOs)
        
        label2 = QLabel('''
        <p>Seleccione la UC de la lista inferior</p>
        ''', self)
        layout.addWidget(label2)
        
        self.comboUCs = QComboBoxModelQuery(self)
        layout.addWidget(self.comboUCs)
        
        self.setLayout(layout)
        self.connect(self.comboCOs, SIGNAL('currentIndexChanged(int)'), 
                     self.update_ucs_for_co)
        
        self.update_ucs_for_co()
        
        QMetaObject.connectSlotsByName(self)
        
    
    def update_ucs_for_co(self):
        co_id = self.comboCOs.get_col_value(1)
        query = QSqlQuery('''
            SELECT CONCAT(UC.nombre_uc, '(' ,UC.id_UC,')'), 
            UC.id FROM UC WHERE UC.co_id = %(co_id)d
        ''' % locals(), qApp.instance().db_con)
        model = QSqlQueryModel(self.comboUCs)
        model.setQuery(query)
        # Deasctivar el siguiente si el CO no tiene UCs
        self.parent().pushNext.setEnabled( query.size() > 0 )
        self.comboUCs.setModel(model)
    
    def on_comboCOs_currentIndexChanged(self, index):
        self.update_ucs_for_co()
    
    
class SeleccionUC(QWidget):
    texto_lineUC = 'Seleccione UC %s'
    def __init__(self, parent):
        print "Creando seleccion de UC"
        QWidget.__init__(self, parent)
        layout = QVBoxLayout(self)
        self.labelUC = QLabel('Seleccione UC', self)
        self.comboUC = QComboBox(self)
        layout.addWidget( self.labelUC )
        layout.addWidget(self.comboUC)
        self.setLayout(layout)
        # Hasta que el usuario no selecciona una UC, no se le deja avanzar
        
        QMetaObject.connectSlotsByName(self)



class ConfiguracionCalles(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
#        layout = QVBoxLayout(self)
        layout = QGridLayout()
        layout.addWidget(QLabel("Configuracion Calles" , self))
        
        self.scene = EsquinaGraphicsScene() 
        self.esquinaConfigView = EsquinaGraphicsView(self.scene)
        
        layout.setRowMinimumHeight(1, 300)
        layout.setColumnMinimumWidth(0, 300)
        layout.addWidget(self.esquinaConfigView,1,0,5,2)
        layout.setRowStretch(1, 1)
        self.setLayout(layout)
        self.parent().pushNext.setEnabled( False )
        self.connect(qApp,SIGNAL("modifiCalle"),self.enableNext)
#        self.parent().pushNext.setEnabled( True )
#   
    def show(self):
        self.scene.estado = EsquinaGraphicsScene.STATE_EDICION_CALLE
        for c in self.scene.calles:
            for s in c.semaforos:
                c.remover_semaforo(s)  
        QWidget.show(self)
  
    def enableNext(self):
        for calle in self.scene.calles:
            if calle.tipo != CalleGraphicsItem.TIPO_CALLE_OUT:
                if calle.nombre == "":
                    self.parent().pushNext.setEnabled( False )
                    return
        self.parent().pushNext.setEnabled( True )
        
class ConfiguracionSemaforos(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
#        layout = QVBoxLayout(self)
        layout = QGridLayout()
        layout.addWidget(QLabel("Configuracion Semaforos"))
       
        db = qApp.instance().db_con   
#    
        id_uc = parent.history[0].comboUCs.get_col_value(1)
#        
        self.table = QTableView()
#        sqlmodel = QSqlQueryModel(self.table)
#        
        query = QSqlQuery('SELECT can_movi FROM UC WHERE id = %d'% id_uc, db)
#        sqlmodel.setQuery( QSqlQuery('SELECT can_movi FROM UC WHERE id = %d'% id_uc, db) )
#        sqlmodel.setQuery( QSqlQuery('SELECT can_movi FROM UC', db) )
#       
        if query.next():
            cant_movi = query.value(0).toInt()[0]
        else:
            log.err("ERROR: el consentrador no tenia cantidad de movis")
        self.model = QStandardItemModel(cant_movi,5)
        self.table.setModel(self.model)
        
        for i in range(cant_movi):
            self.model.setData(self.model.index(i,0),QVariant(i))
        self.table.setItemDelegateForColumn(0,NullDelegate(self.model))
        
        self.listaSemaforos = [('Tres luces', QVariant(Semaforo.TIPO_COMUN)),
                               ('Derecha', QVariant(Semaforo.TIPO_DERECHA)),
                               ('Izquierda', QVariant(Semaforo.TIPO_IZQUIERDA))]
        
        query_sema = QSqlQuery('SELECT * FROM Semaforo WHERE uc_id = %d'% id_uc)
        
        self.semaforos = [Semaforo(n_movi=i) for i in range(cant_movi)]
        
        N_semaforos_n_mov = query_sema.record().indexOf('n_mov')
        N_semaforos_ti_mov = query_sema.record().indexOf('ti_mov')
        
        while query_sema.next():
                
            n_mov = query_sema.value(N_semaforos_n_mov).toInt()[0]        
            ti_mov = query_sema.value(N_semaforos_ti_mov).toInt()[0]
            log.msg("n_mov = %s, ti_mov = %s"% (n_mov,ti_mov))
            if ti_mov:
                tipo = Semaforo.TIPO_PEATONAL
                self.semaforos[n_mov].tipo = tipo
                self.model.setData(self.model.index(n_mov,1), QVariant("Peatonal")) 
                self.model.setData(self.model.index(n_mov,2), QVariant(tipo)) 
         
        def callback(index):
            tipo_sema =  self.model.data(self.model.index(index.row(),index.column()+1))  
            return tipo_sema.toInt()[0] != Semaforo.TIPO_PEATONAL
        
        delegateTachitos = ComboBoxListDelegate(self.listaSemaforos,
                                                callback,
                                                self.model)
        self.table.setItemDelegateForColumn(1,delegateTachitos)
        
        self.connect(delegateTachitos,SIGNAL("changeModelData"),self.changeDataSema)
        self.connect(delegateTachitos,SIGNAL("iluminacionCombobox"),self.iluminaSema)
        
        
        self.scene = parent.history[parent.current_step - 1].scene
        self.scene.estado = EsquinaGraphicsScene.STATE_EDICION_SEMAFOROS 
        
        self.calles = []
        self.listaCalle_ids = []
               
        i = 0
        for calle in self.scene.calles:
            if calle.tipo != CalleGraphicsItem.TIPO_CALLE_OUT:
                self.calles.append(calle)
                self.listaCalle_ids.append((calle.nombre, i))
                i += 1
        
        delegateCalles = ComboBoxListDelegate(self.listaCalle_ids,
                                              ConfiguracionSemaforos.callback_calle(self.model),
                                              self.model)
        
        self.table.setItemDelegateForColumn(3,delegateCalles)  
        
        self.connect(delegateCalles, SIGNAL("changeModelData"),self.changeDataCalle)
        self.connect(delegateCalles, SIGNAL("iluminacionCombobox"),self.iluminaCalle)
              
#        self.table.setItemDelegateForColumn(3,CalleComboBoxDelegate(self.calles,
#                                                               self.model))
        self.model.setHeaderData(0,Qt.Horizontal,QVariant(u"N° de Movimiento"))
        self.model.setHeaderData(1,Qt.Horizontal,QVariant("Tipo"))
        self.model.setHeaderData(3,Qt.Horizontal,QVariant("Calle"))
#        self.table.resizeColumnsToContents()
        self.table.hideColumn(2)
        self.table.hideColumn(4)
        
        layout.setRowMinimumHeight(1,150)
        layout.addWidget(self.table,1,0,4,3)
        
        self.esquinaConfigView = EsquinaGraphicsView(self.scene)
        self.esquinaConfigView.setScene(self.scene)
        
        layout.setRowMinimumHeight(5, 300)
        layout.addWidget(self.esquinaConfigView,5,0,5,2)
#        layout.setRowStretch(3, 3)
        self.setLayout(layout)
    
    class callback_calle():
        def __init__(self, model):
            self.model = model
            
        def __call__(self, index):
            tipo_sema =  self.model.data(self.model.index(index.row(),index.column()-1))  
            return tipo_sema.type() != QVariant.Invalid
        
    def changeDataSema(self,id,index):
        sema = self.semaforos[index.row()]
        if id.isValid():
            log.msg('el tipo de semaforo es valido')
            sema.tipo = id.toInt()[0]
            sema.update()
        else:
            log.msg('el tipo de semaforo NO es valido')
        self.insertar_semaforo(index.row())
        
        

    def iluminaSema(self,index):
        log.msg("se esta seleccionando el tipo sema, index = %d "%index)

    def changeDataCalle(self,index_arreglo,index):
        #apago todas las calles que estan iluminadas
        for i in range(len(self.calles)):
            self.calles[i].hover = False
            self.calles[i].setZValue(1)
            self.calles[i].update()
        self.insertar_semaforo(index.row())
        pass
    
    def iluminaCalle(self,index):
        ind = index-1
        for i in range(len(self.calles)):
            if i == ind:
                self.calles[i].hover = True
                self.calles[i].setZValue(2)
                self.calles[i].update()
            else:
                self.calles[i].hover = False
                self.calles[i].setZValue(1)
                self.calles[i].update()
                
    def insertar_semaforo(self, row):
        columna_tipo_sema =  self.model.data(self.model.index(row,2))
        columna_calle_index = self.model.data(self.model.index(row,4))
        s = self.semaforos[row]
        if s.creador:
            cc = s.creador
            cc.remover_semaforo(s)
        if columna_tipo_sema.isValid() and columna_calle_index.isValid():
            tipo_sema = columna_tipo_sema.toInt()[0]
            calle_index = columna_calle_index.toInt()[0]
            c = self.calles[calle_index]
            s.tipo = tipo_sema
            c.insertar_semaforo(semaforo = s)
            log.msg("se inserto el semaforo")
        else:
            log.msg("no se inserta el semaforo porque faltan datos")
        
if __name__ == '__main__':
    from qt_dbhelp import dburl_to_qsqldb
    app = QApplication([])
    app.db_con = dburl_to_qsqldb('mysql://dsem:passmenot@localhost:3306/dsem')
    win = EsquinaConfigWizard(None)
    win.show()
    app.exec_()