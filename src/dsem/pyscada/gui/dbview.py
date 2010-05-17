#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from dsem.picnet.bitfield import bitfield
from pyscada.gui.delegates import *
from pyscada.gui.qt_dbhelp import PyQSqlQuery
from pyscada.smfparse import parse_smf
from twisted.python import log
import os
                
class TableViewEventMenu(QTableView):
    '''
    Table view para los eventos de alta prioridad donde tenemos una menu
    contextual.
    '''
    def __init__(self, parent):
        QTableView.__init__(self, parent)
        self.setup_actions()
        self.setup_menus()
        QMetaObject.connectSlotsByName(self)
        
    def setup_actions(self):
        self.actionAtencion = QAction(self.trUtf8('Atencion'), self)
        self.actionAtencion.setObjectName('actionAtencion')
        
    
    def setup_menus(self):
        self.menu = QMenu(self)
        self.menu.addAction(self.actionAtencion)
    
    def contextMenuEvent(self, event):
        pass


class QTableViewActionsMenu(QTableView):
    def __init__(self, parent = None):
        QTableView.__init__(self, parent)
        self.setup_actions()
        self.setup_menu()
        QMetaObject.connectSlotsByName(self)
        
    def setup_actions(self):
        pass
    
    def setup_menu(self):
        self.menu = QMenu(self)
        for action in self.actions():
            self.menu.addAction(action)
            
    def contextMenuEvent(self, event):
        '''
        Cuando se hace click derecho sobre la fila.
        '''
        row_num = self.rowAt(event.pos().y())
        self.selectRow( row_num )
        self._current_row = row_num
        # Eviar que se cuelgue ante una edicion
        self.reset()
        if self.menu.actions():
            self.menu.exec_(self.mapToGlobal(event.pos()))
            
    def refresh_table(self):
        ''' Refrescar la tabla sin perder el valor del scroll '''
        model = self.model()
        if not model:
            return
        scroll = self.verticalScrollBar().value()
        if type(model) == QSqlTableModel:
            model.select()
        elif type(model) == QSqlQueryModel or isinstance(model, QSqlQueryModel):
            query = model.query()
            if query.exec_():
                model.setQuery(query)
        else:
            log.err("No se refrescar %s" % model)
        self.resizeRowsToContents()
        self.verticalScrollBar().setValue(scroll)
        self.dirty = False
    
    # TODO: Refresco intelignete    
    _dirty = False
    def dirty(): #@NoSelf
        doc = """Marcar la tabla para refrescar cuando tiene foco""" #@UnusedVariable
        def fget(self):
            return self._dirty
           
        def fset(self, value):
            self._dirty = value
            
        return locals()
       
    dirty = property(**dirty())
    
    def showEvent(self, event):
        if self.dirty:
            self.refresh_table()
            
        #QTableViewActionsMenu.showEvent(self, event)
    
    def do_update(self):
        ''' Este método se llama desde afuera para avisar que la tabla está sucia '''
        if self.isVisible():
            self.refresh_table()
        else:
            self.dirty = True
            
class QTableViewHighPrio(QTableViewActionsMenu):
    '''
    Tabla para los eventos de alta prioridad
    Trabaja en conjunto con EventoColorBgSqlQueryModel.
    '''
    
    
    def setup_actions(self):
        self.actionAtender = QAction(self.trUtf8('Establecer atención'), self)
        self.actionAtender.setObjectName('actionAtender')
        
        self.actionReparar = QAction(self.trUtf8('Establecer como reparado'), self)
        self.actionReparar.setObjectName('actionReparar')

    

        
    @pyqtSignature('')
    def on_actionAtender_triggered(self):
        if not self.current_ev_id:
            return
        
        r = QMessageBox.question(self, "Desea atender este evento?",
                             "Desea atender este evento?",
                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if r == QMessageBox.Yes:
            
            query = PyQSqlQuery()
            query.prepare("UPDATE EV SET EV.ts_a = ?, EV.atendido = 'o' WHERE id = %d" % self.current_ev_id )
            query.bindValue(0, QVariant(QDateTime.currentDateTime()))
            query.exec_()
            query.exec_('''SELECT co_id, id_UC from UC INNER JOIN EV 
                        ON EV.uc_id = UC.id WHERE EV.id = %d''' % self.current_ev_id )
            qApp.instance().emit(SIGNAL('event_attended(int, int)'), query.co_id, query.id_UC)
            log.msg('Atencion %s' % (query.lastError().databaseText() or "OK"))
            # Actualizar
            self.refresh_table()
            
            
        
    @pyqtSignature('')
    def on_actionReparar_triggered(self):
        r = QMessageBox.question(self, "Desea establacer este evento como reparado?",
                             "Desea establacer este evento como reparado?",
                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if r == QMessageBox.Yes:
            if r == QMessageBox.Yes:
                
                query = QSqlQuery()
                query.prepare("UPDATE EV SET EV.ts_r = ?, EV.atendido = 'r' WHERE id = %d" % self.current_ev_id)
                query.bindValue(0, QVariant(QDateTime.currentDateTime()))
                query.exec_()
                log.msg('Reparacion %s' % (query.lastError().databaseText() or "OK"))
                # Actualizar
                self.refresh_table()
                
    def setup_menu(self):
        QTableViewActionsMenu.setup_menu(self)
        self.menu.addAction(self.actionAtender)
        self.menu.addAction(self.actionReparar)
        
    def contextMenuEvent(self, event):
        '''
        Cuando se hace click derecho sobre la fila.
        Establecer las acciones disponibles: Reparación y Notificación.
        '''
        row_num = self.rowAt(event.pos().y())
        self.selectRow( row_num )
        self._current_row = row_num
        
        query = PyQSqlQuery(self.model().query())
        query.seek(row_num)
        self.current_ev_id = query.ev_id
        
        
        # Eviar que se cuelgue ante una edicion
        # TODO: Fijarse en esto. Falta desahbilitar bien cuando no hay eventos.
        self.reset()
        if not self.current_ev_id: 
            self.actionAtender.setEnabled(False)
            self.actionReparar.setEnabled(False)
        
        if not self.model().index(row_num, self.model().index_ts_a ).data().toDate():
            self.actionAtender.setEnabled(True)
            self.actionReparar.setEnabled(False)
        elif not self.model().index(row_num, self.model().index_ts_r ).data().toDate():
            self.actionAtender.setEnabled(False)
            self.actionReparar.setEnabled(True)
        else:
            self.actionAtender.setEnabled(False)
            self.actionReparar.setEnabled(False)
        
        if self.menu.actions():
            self.menu.exec_(self.mapToGlobal(event.pos()))
    
    

class QTableViewLowPrio(QTableViewActionsMenu):
    '''
    Tabla para los eventos de baja prioridad
    '''
    pass

class QTableRefreshAction(QTableViewActionsMenu):

    def setup_menu(self):
        self.menu = QMenu(self)
        self.menu.addAction(self.actionRefresh)

    def setup_actions(self):
        self.actionRefresh = QAction(self.trUtf8('Refrescar'), self)
        self.actionRefresh.setObjectName('actionRefresh')
        

    @pyqtSignature('')
    def on_actionRefresh_triggered(self):
        model = self.model()
        if model:
            model.select()
            #self.resizeColumnsToContents()
            self.resizeRowsToContents()
    
    def commitData(self, editor):
        QTableView.commitData(self, editor)
        self.resizeRowsToContents()
    
        #void QAbstractItemView::rowsInserted 
        #( const QModelIndex & parent, int start, int end )   [virtual protected slot]
     
    def _rowsInserted (self, parent, start, end ):
        log.msg('Row Inserted')
        QTableView.rowsInserted(self, parent, start, end)


    
class QTableCO(QTableRefreshAction):
    '''
    Vista de tabla para los concentradores
    '''
    _tableUC = None
    
    def tableUC(): #@NoSelf
        doc = """Referencia a la TableView""" #@UnusedVariable
       
        def fget(self):
            return self._tableUC
           
        def fset(self, value):
            log.msg('Seteo de tabla de UC')
            self._tableUC = value
           
        return locals()
    tableUC = property(**tableUC())

    def setModel(self, model):
        QTableView.setModel(self, model)
        #self.hideColumn(model.fieldIndex('id'))
        model.setEditStrategy( QSqlTableModel.OnFieldChange )
        self.setEditTriggers( QAbstractItemView.DoubleClicked  )
        index_id_co = model.fieldIndex('id_CO')
        model.setHeaderData(index_id_co, Qt.Horizontal, 
                            QVariant(u'N°'))
        log.msg('Setenado el delegate para %d' % index_id_co)
        self.setItemDelegateForColumn(index_id_co, IntegerRangeDelegate(1,
                                                                        254,
                                                                        1,
                                                                        model))
        
        ip_address_index = model.fieldIndex('ip_address')
#        self.setItemDelegateForColumn(ip_address_index, IPAddressTextDelegate(
#                                                                              parent = model))
        self.setItemDelegateForColumn(ip_address_index, IPAddressLooseDelegate(
                                                                              model = model,
                                                                              parent = model))
        model.setHeaderData(ip_address_index, Qt.Horizontal, 
                            QVariant(u'Dirección IP'))
        
        index_hab = model.fieldIndex('hab')
        self.setItemDelegateForColumn(index_hab, BooleanDelegate(model))
        model.setHeaderData(index_hab, Qt.Horizontal, 
                            QVariant(u'Habilitado'))
        
        max_retry_index = model.fieldIndex('max_retry')
        self.setItemDelegateForColumn(max_retry_index, IntegerRangeDelegate(0,
                                                                            10,
                                                                            5,
                                                                            model))
        model.setHeaderData(max_retry_index, Qt.Horizontal, 
                            QVariant(u'Cantidad de reintentos'))
        
        t_out_index = model.fieldIndex('t_out')
        self.setItemDelegateForColumn(t_out_index, FloatRangeDelegate(
                                                                      0.25,
                                                                      60,
                                                                      5,
                                                                      model
                                                                      ))
        
        model.setHeaderData(t_out_index, Qt.Horizontal, 
                            QVariant(u'Tiempo fuera'))
        

        poll_delay_index = model.fieldIndex('poll_delay')
        
        self.setItemDelegateForColumn(poll_delay_index, FloatRangeDelegate(
                                                                           0.2,
                                                                           60,
                                                                           3,
                                                                           model
                                                                           ))
        model.setHeaderData( poll_delay_index , Qt.Horizontal, 
                            QVariant(u'Tiempo entre consulta'))
        
        # Este tiempo no se usa
        #t_poll_index = model.fieldIndex('t_poll')
        #self.setItemDelegateForColumn(t_poll_index, FloatRangeDelegate(0,
        #                                                               1200,
        #                                                               5,
        #                                                               model))
        #model.setHeaderData(t_poll_index, Qt.Horizontal, 
        #                    QVariant(u'Tiempo entre consultas'))
    
        # 
    #void QAbstractItemView::dataChanged ( const QModelIndex & topLeft, const QModelIndex & bottomRight )   [virtual protected slot]
    def dataChanged(self, topLeft, bottomRight):
        print "Data changed"
        self.resizeRowsToContents()
        
    def setup_actions(self):
        super(QTableCO, self).setup_actions()
        
        self.actionRemove = QAction(self.trUtf8('Eliminar Concentrador'), self)
        self.actionRemove.setObjectName('actionRemove')
        
        self.actionFilterUCs = QAction(self.trUtf8('Mostrar solo UCs de este Concentrador'),self)
        self.actionFilterUCs.setObjectName('actionFilterUCs')
        
        
    def setup_menu(self):
        super(QTableCO, self).setup_menu()
        self.menu.addAction(self.actionFilterUCs)
        self.menu.addSeparator()
        self.menu.addAction(self.actionRemove)
        
        
    @pyqtSignature('')
    def on_actionRemove_triggered(self):
        resp = QMessageBox.question(self, self.trUtf8('Eliminar el concentrador?'),
                             self.trUtf8("Seguro que desea eliminar el concentrador"),
                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                             QMessageBox.Cancel)
        if resp == QMessageBox.Yes:
            self.model().removeRow( self._current_row )
    
    
class QTableUC(QTableRefreshAction):
    '''
    Vista de tabla para las unidades de control
    '''
    def setModel(self, model):
        QTableRefreshAction.setModel(self, model)
        model.setEditStrategy( QSqlTableModel.OnFieldChange )
        self.setEditTriggers( QAbstractItemView.DoubleClicked )
        
        self.hideColumn(model.fieldIndex('id'))
        
        
        
        model.setHeaderData(model.fieldIndex('nombre_uc'), Qt.Horizontal, 
                            QVariant(u'Ubicación'))
        
        
        id_UC_index = model.fieldIndex('id_UC')
        model.setHeaderData(id_UC_index, Qt.Horizontal, 
                            QVariant(u'N° UC'))
        
        self.setItemDelegateForColumn(id_UC_index, IntegerRangeDelegate(2,
                                                                       63,
                                                                       1,
                                                                       model
                                                                       ))
        
        zona_index = model.fieldIndex('zona')
        self.setItemDelegateForColumn(zona_index, IntegerRangeDelegate(1,
                                                                       63,
                                                                       1,
                                                                       model
                                                                       ))
        
        can_movi_index = model.fieldIndex('can_movi')
        self.setItemDelegateForColumn(can_movi_index, NullDelegate(model))
        
        model.setHeaderData(can_movi_index, Qt.Horizontal, 
                            QVariant(u'Cantidad de Movimientos'))
        
        hab_index = model.fieldIndex('hab')
        self.setItemDelegateForColumn(hab_index, BooleanDelegate(model))
        model.setHeaderData(hab_index, Qt.Horizontal, 
                            QVariant(u'Habilitado'))
        co_id_index = model.fieldIndex('co_id')
        self.setItemDelegateForColumn(co_id_index, QSqlRelationalDelegate(model))
        model.setHeaderData(co_id_index, Qt.Horizontal, 
                            QVariant(u'Concentrador'))
        
        
    def setup_actions(self):
        super(QTableUC, self).setup_actions()
        
        self.actionAddUC = QAction(self.trUtf8('Agregar Unidad de Control'), self)
        self.actionAddUC.setToolTip('Agregar Unidad de Control')
        self.actionAddUC.setIcon(QIcon(':/icons/res/list-add.png'))
        self.actionAddUC.setObjectName('actionAddUC')
        
        self.actionFilterReset = QAction(self.trUtf8('Mostrar todos'), self)
        self.actionFilterReset.setToolTip('Mostar todas las unidades de control')
        self.actionFilterReset.setObjectName('actionFilterReset')
        self.actionFilterReset.setIcon(QIcon(':/icons/res/transform-rotate.png'))
        self.actionFilterReset.setEnabled(False)
        
        self.actionRemoveUC = QAction(self.trUtf8('Quitar UC'), self)
        self.actionRemoveUC.setObjectName('actionRemoveUC')
        
    def setup_menu(self):
        super(QTableUC, self).setup_menu()
        self.menu.addAction(self.actionRemoveUC)
        
    
    @pyqtSignature('')
    def on_actionAddUC_triggered(self):
        '''
        Añadir una UC mediante un archivo SMF del configurador de Ricardo.|
        '''
        #self.model().insertRecord(-1, QSqlRecord())
        smfs = QFileDialog.getOpenFileNames(None, 'Seleccione lo(s) archivo(s) SMF',
                                                '', u'Archivo de configuración de semaforización (*.smf *.SMF)')
        ok, error = 0, 0
        if smfs:
            for smf in smfs:
                smf = str(smf) # QString -> str
                try:
                    smf_data = parse_smf(smf)
                    if not smf_data:
                        QMessageBox.warning(None, "No se pudo abrir %s" % smf, "Error: No se pudede abrir %s" % smf)
                        continue
                    nombre = os.path.splitext(os.path.split(smf)[1])[0]
                    query = PyQSqlQuery('''INSERT INTO UC (co_id, id_UC, zona, can_movi, nombre_uc, hab) VALUES
                                                          (%d, %d, %d, %d, '%s', %d)  ''' %
                                                            (smf_data['id_CO'], smf_data['id_UC'], smf_data['Zona'],
                                                             smf_data['CanMovi'], nombre, 1) #Iniciamos el concentrador en 1
                                                            )
                    if query.lastError().isValid():
                        QMessageBox.warning(None, "No se pudo abrir %s" % smf, "Error en inserción en la DB de %s" % nombre)
                        log.err(str(query.lastError().databaseText()))
                    else:
                        uc_id = query.lastInsertId().toInt()[0]
                        log.msg("id UC insertado %d." % uc_id)
                        # String -> Entero
#                        log.msg((smf_data['timovH'], smf_data['timovL']))
#                        timov_bytes = map(lambda i: int(i, 16), (smf_data['timovH'], smf_data['timovL']))
#                        
#                        [smf_data['timovH'], smf_data['timovL']]
                        #timov = timov_h << 8 + timov_l
                        timov = bitfield([smf_data['timovH'], smf_data['timovL']])
                        for n_mov in range(smf_data['CanMovi']):
                            query.exec_('''INSERT INTO Semaforo (uc_id, ti_mov, n_mov) 
                                                            VALUES  ( %d, %d, %d)''' %
                                                            (uc_id, timov[n_mov], n_mov)
                                            )
                            log.msg(str((uc_id, timov[n_mov], n_mov)))
                            if query.lastError().isValid():
                                log.err("Insertando semaforo ocurrio: %s" % str(query.lastError().databaseText()))
                            else:
                                sem_id = query.lastInsertId().toInt()[0]
                                log.msg("Insertado Semaforo: %d" % sem_id)
                        
                    ok += 1
                    
                except IOError:
                    QMessageBox.warning(None, "No se pudo abrir %s" % smf, "Error: No se pudede abrir %s" % smf)
                    error += 1
                
            self.refresh_table()
                    
        log.msg('SMF cargados %d, erroneos: %d' % (ok, error))
    
    @pyqtSignature('')
    def on_actionRemoveUC_triggered(self):
        log.msg('Quitar UC fina %d' % self._current_row)
        resp = QMessageBox.question(self, self.trUtf8('Eliminar la UC?'),
                             self.trUtf8("Seguro que desea eliminar la UC?"),
                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                             QMessageBox.Cancel)
        if resp == QMessageBox.Yes:
            uc_id = self.model().data(self.model().index(self._current_row,self.model().fieldIndex('id'))).toInt()[0]
            log.msg('Quitando UC de la DB id = %d' % uc_id)
            query = PyQSqlQuery()
            
            transaction = qApp.instance().db_con.transaction()
            log.msg('Inicio de la tranasccion? %s' % transaction)
            try:
                query_esquinas_uc = QSqlQuery('SELECT id FROM Esquina WHERE uc_id = %d'% uc_id)
                while query_esquinas_uc.next():
                    esquina_id = query_esquinas_uc.value(0).toInt()[0]
                    log.msg('Se van a borrar la Esquina_Calles')
                    query.exec_('DELETE FROM Esquina_Calles WHERE esquina_id = %d'% esquina_id)         
                    log.msg('El id de la esquina a borrar es = %d'%esquina_id)         
                    query.exec_('DELETE FROM Esquina WHERE Esquina.id = %d' % esquina_id)
                    log.msg("%s" % query.lastError().databaseText() or "OK")
                log.msg('Se van a borrar los semaforos')
                query.exec_('DELETE FROM Semaforo WHERE uc_id = %d'% uc_id)                             
                self.model().removeRow( self._current_row )
            
                if not query.lastError().type() == QSqlError.NoError:
                    if transaction:
                        qApp.instance().db_con.rollback()
                    log.err('Error en la DB: %s' % query.lastError().databaseText())
                else:
                    if transaction:
                        commit = qApp.instance().db_con.commit()
                        log.msg('Commit exitoso %s' % commit)
            except Exception, e:
                log.err(str(e))
                if transaction:
                    qApp.instance().db_con.rollback()

    