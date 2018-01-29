#! /usr/bin/env python
# -*- encoding: utf-8 -*-


from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
from PyQt4.QtSql import * #@UnusedWildImport
from qt_dbhelp import dburl_to_qsqldb

class DataBrowser(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setWindowTitle('Data Browser')
        self.__connection = None
        self.setup_ui()
        
    def setup_ui(self):
        '''
        Setup the layout
        '''
        self._layout = QVBoxLayout(self)
        self._layout.setMargin(3)
        
        self._tableView = QTableView(self)
        self._tableView.setObjectName('tableView')
        self._layout.addWidget(self._tableView)
        
        self.buttonNext = QPushButton(self.trUtf8("&Next »"))
        self.buttonNext.setObjectName('buttonNext')
        
        self.buttonPrev = QPushButton(self.trUtf8("« &Previous"))
        self.buttonPrev.setObjectName('buttonPrev')
        
        self.buttonFirst = QPushButton(self.trUtf8("|« &First"))
        self.buttonFirst.setObjectName('buttonFirst')
        
        self.buttonLast = QPushButton(self.trUtf8("&Last »|"))
        self.buttonLast.setObjectName('buttonLast')
        
        self._buttonLayout = QHBoxLayout(self)
        self._buttonLayout.setMargin(0)
        
        spacerItem = QSpacerItem(688, 20, QSizePolicy.Expanding, 
                                                QSizePolicy.Minimum)
        self._buttonLayout.addItem(spacerItem)
        self._buttonLayout.addWidget(self.buttonFirst)
        self._buttonLayout.addWidget(self.buttonPrev)
        self._buttonLayout.addWidget(self.buttonNext)
        self._buttonLayout.addWidget(self.buttonLast)
        
        self._layout.addLayout(self._buttonLayout)
        #self._buttonLayout.hide()
        self.setLayout(self._layout)
    
    def connection(): #@NoSelf
        def fget(self):
            return self.__connection
        def fset(self, value):
            if type(value) == str:
                self.__connection = dburl_to_qsqldb(value)
            elif type(value) == QSqlDatabase:
                self.__connection == value
            else:
                raise TypeError("%s is not either QSqlDatabase nor a DB url" % value)
        return locals()
    connection = property(**connection())
    
    # ------------------------------------------------------------------------
    # Methods for showing data
    # ------------------------------------------------------------------------
    
    def show_table(self, table_name):
        assert self.connection is not None, "Falta la conexion"
        self._model = QSqlTableModel(self, self.connection)
        self._model.setTable(table_name)
        self._model.select()
        self._tableView.setModel(self._model)
    
    def show_query(self, query):
        pass
    
    def show_model(self, model):
        pass
    
    def model(): #@NoSelf
        def fget(self):
            return self._tableView.model()
        def fset(self, value):
            self._tableView.setModel(model)
            self._update_findex()
        return locals()
    model = property(**model())
    
    
    def _update_findex(self):
        if type(self.model) == QSqlTableModel:
            findex = lambda self, name: self.model.fieldIndex(name)
        elif type(self.model) == QSqlQueryModel:
            findex = lambda self, name: self.model.record().indexOf(name)
        self.findex = findex

    def set_header_data(self, header_dict):
        '''
        Set
        '''
        for field_name, header_label in header_dict.iteritems():
            try:
                index = type(field_name) == str and self.findex( field_name ) or field_name
                self.model.setHeaderData(index, Qt.Horizontal, QVariant(
                    header_label
                ))
            except Exception, e:
                print e
                    
    def add_row(self, cant = 1):
        # Insertar fila
        try:
            self.model.addRows(self.model.count(), cant)
        except Exception, e:
            pass


class QColorTableModel(QSqlQueryModel):
    '''
    Colores en la tabla
    '''
    def beginInsertRows(self, index, start, end):
        QSqlQueryModel.beginInsertRows(self, index, start, end)
        print "Begin insert rows"

class EditorCalles(QWidget):
    
    class TableView(QTableView):
        def __init__(self, parent = None):
            QTableView.__init__(self, parent)
            self.setMouseTracking(True)
            self.current_id = 0
            
        def mouseMoveEvent(self, event):
            
            tabla = self.parent().tablaCalles
            fila = tabla.rowAt(event.pos().y())
            id = tabla.model().data( tabla.model().index(fila, 0)).toInt()[0]
            if id != self.current_id:
                self.current_id = id
                query = QSqlQuery('SELECT nombre FROM Calle WHERE id = %d' % id)
                if query.next():
                    calle = query.value( query.record().indexOf('nombre') ).toString()
                    tabla.setToolTip(u'%s' % calle)
            
            return QTableView.mouseMoveEvent(self, event)
        
        def selectionChanged(self, new,  old):
            print "Cambio de seleccion", new.indexes()
            QTableView.selectionChanged(self, new, old)
        
    class CallesQSqlQuery(QSqlQuery):
        def __init__(self, db = None, where = ''):
            if not db:
                db = qApp.db_con
            sql = u'''
                SELECT
         
                    Calle.id `N°`, 
                    Calle.nombre `Nombre de la Calle`, 
                    count(Esquina_Calles.id) `Cantidad de Esquinas asociadas` 
                
                FROM Calle 
                LEFT JOIN Esquina_Calles 
                ON Esquina_Calles.calle_id = Calle.id
                %s
                GROUP BY Calle.nombre
                
            ''' % where
            #print sql
            QSqlQuery.__init__(self, sql, db)
            #print self.lastError().databaseText()
            #print self.numRowsAffected()
            
    def __init__(self):
        QWidget.__init__(self)
        self.setup_ui()
        self.setup_model()
        self.resize(self.contentsRect().size())
        self.setWindowTitle(u"Edición de Calles")
        
        QMetaObject.connectSlotsByName(self)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setMargin(4)
        
        layout_filtro = QHBoxLayout(None)
        layout_filtro.addWidget(QLabel("Filtro:"))
        
        self.lineFiltro = QLineEdit(self)
        self.lineFiltro.setObjectName('lineFiltro')
        layout_filtro.addWidget( self.lineFiltro )
        
        self.buttonLimpiarFiltro = QPushButton('&Limpiar', self)
        self.buttonLimpiarFiltro.setObjectName('buttonLimpiarFiltro')
        layout_filtro.addWidget(self.buttonLimpiarFiltro)
        self.connect(self.buttonLimpiarFiltro, SIGNAL('pressed()'),
                     self.lineFiltro, SLOT('clear()'))
        
        layout.addLayout(layout_filtro)
        
        self.tablaCalles = EditorCalles.TableView(self) 
        #self.tablaCalles = QTableView(self)
        self.tablaCalles.setObjectName('tablaCalles')
        layout.addWidget(self.tablaCalles)
        
        layout_botones = QHBoxLayout(None)
        layout_botones.setSpacing(2)
        
        
        self.buttonNuevo = QPushButton( self )
        self.buttonNuevo.setToolTip(u'Crear Nueva Calle')
        self.buttonNuevo.setObjectName( 'buttonNuevo' )
        self.buttonNuevo.setIcon(QIcon(':/icons/res/list-add.png'))
        self.buttonNuevo.setIconSize(QSize(32,32))
        layout_botones.addWidget( self.buttonNuevo )
        
        self.buttonEditar = QPushButton( self)
        self.buttonEditar.setToolTip(u'Editar la calle seleccionada')
        self.buttonEditar.setIcon(QIcon(':/icons/res/draw-freehand.png'))
        self.buttonEditar.setIconSize(QSize(32,32))
        self.buttonEditar.setObjectName( 'buttonEditar' )
        layout_botones.addWidget( self.buttonEditar )
        
        self.buttonSuprimir = QPushButton( self )
        self.buttonSuprimir.setToolTip(u'Suprimir la calle seleccionada')
        self.buttonSuprimir.setIcon(QIcon(':/icons/res/draw-eraser.png'))
        self.buttonSuprimir.setIconSize(QSize(32,32))
        self.buttonSuprimir.setObjectName( 'buttonSuprimir' )
        layout_botones.addWidget( self.buttonSuprimir )
        
        
        self.buttonCerrar = QPushButton( 'Cerrar', self)
        #self.buttonCerrar.setObjectName( 'buttonCerrar' ) # Connect manual
        self.buttonCerrar.setIcon(QIcon(':/icons/res/dialog-error.png'))
        self.buttonCerrar.setIconSize(QSize(32,32))
        layout_botones.addWidget( self.buttonCerrar )
        self.connect(self.buttonCerrar, SIGNAL('pressed()'), self.close)
        
        layout_botones.insertStretch(layout_botones.count()  -1 )
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def on_lineFiltro_textChanged(self, text):
        model = self.tablaCalles.model()
        if text:
            query = EditorCalles.CallesQSqlQuery(None, "WHERE Calle.nombre LIKE '%%%s%%'" % text)
        else:
            query = EditorCalles.CallesQSqlQuery()
        model.setQuery(query)
        
    
    def setup_model(self):
        query = EditorCalles.CallesQSqlQuery(qApp.db_con)
        model = QSqlQueryModel(self.tablaCalles)
        model.setQuery(query)
        self.tablaCalles.setModel(model)
        self.tablaCalles.resizeColumnsToContents()

class EventoColorBgSqlQueryModel(QSqlQueryModel):
    ''' Este modelo cambia el color en funcion de si el evento es atendido 
        o no '''
    COLOR_NO_ATENDIDO = QBrush(QColor(0xFF, 0x65, 0x3A))
    COLOR_ATENDIDO = QBrush(QColor(0xAE, 0xE9, 0xFF))
    COLOR_REPARADO = QBrush(QColor(0x56, 0xFF, 0x50))
    
    def __init__(self, *largs):
        QSqlQueryModel.__init__(self, *largs)
        self.setQuery(QSqlQuery('SELECT * FROM EV'))
        
    
    def setQuery(self, *largs):
        QSqlQueryModel.setQuery(self, *largs)
        self.index_ts_a = self.record().indexOf('ts_a')
        self.index_ts_r = self.record().indexOf('ts_r')
        
        
    def data(self, index, role):
        # Obtenemos el valor real
        value = QSqlQueryModel.data(self, index, role)
        
        if role == Qt.BackgroundColorRole:
            # Está atendido?
            if not index.sibling(index.row(), self.index_ts_a).data().toDate():
                # No atendido, Es ROJO
                return QVariant(self.COLOR_NO_ATENDIDO)
            elif not index.sibling(index.row(), self.index_ts_r).data().toDate():
                # Atendido y no reparado
                return QVariant(self.COLOR_ATENDIDO)
            else:
                return QVariant(self.COLOR_REPARADO)
            
        return value
    
    
if __name__ == '__main__':
    import sys
    sys.path += ('..', '../..')
    app = QApplication(sys.argv)
    from pyscada.gui.qt_dbhelp import dburl_to_qsqldb
    try:
        # Se lo chantamos así nomás
        qApp.db_con = dburl_to_qsqldb('mysql://dsem:passmenot@localhost:3306/dsem')
        q = QSqlQuery("SET NAMES 'utf8'", qApp.db_con)
        print q.exec_()
        
    except Exception, e:
        import traceback
        QMessageBox.critical(None, "Error", u"<h2>%s</h2></pre>%s</pre>" %
                             (type(e), traceback.format_exc()))
        sys.exit()
    import data_rc #@UnresolvedImport
    #QTextCodec.setCodecForLocale ( QTextCodec.codecForName ( "UTF-8" ) ) 

    # Edior de calles WIP
    #win = EditorCalles()
    
    
    win = QTableView()
    win.setModel(EventoColorBgSqlQueryModel(win))

    #model = QSqlTableModel(win)
    #model.setTable('EV')
    #model.select()
    #win.setModel( model )
    
    win.resize(win.contentsRect().size())
    win.show()    
    app.exec_()