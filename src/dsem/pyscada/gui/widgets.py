#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from PyQt4.QtGui import QComboBox
from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtSql import QSqlRecord


class QComboBoxModelQuery(QComboBox):
    '''
    QComboBox que tiene métodos para buscar el valor de un campo del modelo
    del cual toma datos.
    '''
    
    def query_str(self):
        return u"«%s»" % str(self.model().query().lastQuery()).upper()
    
    def get_col_value(self, col = 1 ):
        '''
        Busca el valor de un campo.
        '''
        #print self.query_str()
        
        model = self.model()
        if not model:
            raise ValueError('%s No tiene modelo.' % self)
        
        query = model.query()
        
        if query.record().count() < col:
            raise Exception("Es necesrario mas de un campo %d" % self.model().record().count())
        
        #TODO: Implementar esta validación
        #if not isinstance(self.model(), QSqlQueryModel):
        #    print "no sqlquery"
        #    raise ValueError('El modelo de %s no es sublcase de QSqlQueryModel.' % self)
        
        ok = query.seek( self.currentIndex() )
        if ok:
            qvar = query.value(col)
            if qvar.type() == QVariant.Int:
                val, ok = qvar.toInt()
            elif qvar.type() == QVariant.String:
                return str(qvar.toString())
            else:
                QMessageBox(None, 'Obtener valor de columna', 'Al tipo del QVariant recuperado por get_col_val en widgets.py no se le ha definido conversion')
            return val
        else:
            raise Exception("No se puede buscar el indice en el modelo")
            
    def search_by_text(self):
        '''
        Este método busca mediante el texto acutal, pero en un combobox no
        con el currentIndex es suficiente para saber la posicion sobre el
        cursor de la query. Es necesario que en el modelo se halla incluido
        el ID dentro de los campos buscados.
        '''
        model_col = self.modelColumn()
        print "model", model_col
        model_index = self.model().index(0,model_col)
        print "model index", model_index
        print "Buscando texto", self.currentText() 
        value = QVariant(self.currentText())
        print "VALOR => ", value
        
        
        
        match_index = self.model().match(model_index, # Indice columna busqueda 
                                  Qt.EditRole,  # Rol
                                  value,  # Texto a encontrar
                                  1 # Cantida de veces a encontrar
                                  )[0]
                                  
        print "Buscando valor"
        val = self.model().data( self.model().index(match_index.row(), 
                                col) )
        
        #print "Buscar tipo"
        type = val.type()
        if type == QVariant.Invalid:
            return None
        if type == QVariant.Int:
            return val.toInt()[0]
        elif type == QVariant.String:
            return str(val.toString())
        #print "Volvemos"
    
        return val
    

# -----------------------------------------------------------------------------
# Código de prueba
# -----------------------------------------------------------------------------
def show_query(sql_query):
    assert type(sql_query) is QSqlQuery
    
    #sql_query.exec_()
    field_text_length=15
    record = sql_query.record()
    cant_fields = record.count()
    
    print '=' * (field_text_length * cant_fields) 
    for i in xrange(cant_fields):
        print "%-15s" % record.fieldName(i),
    print
    print '=' * (field_text_length * cant_fields)
    indexes = range(cant_fields)
    
    if not sql_query.isValid():
            sql_query.next()
            
    while True:
        
        for i in indexes:
            value = record.value(i)
            #print "%-15s" % value.toString(), 
            print value.type(), i,
        print
        sql_query.next()
        if not sql_query.isValid():
            break



if __name__ == "__main__":
    # Código de prueba
    
    
    from PyQt4.QtGui import QApplication, qApp, QMessageBox
    from PyQt4.QtCore import SIGNAL
    from PyQt4.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
    import sys
    app = QApplication([])
    
    
    def setup_db_sqlite():
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(":memory:")
        if not db.open():
            QMessageBox.critical(None, "No se puede acceder", "No se puede acceder a la DB")
            sys.exit(2)
            
        query = QSqlQuery() # Toma la DB definida...
        query.exec_("create table person(id int primary key, "
                    "firstname varchar(20), lastname varchar(20))")
        query.exec_("insert into person values(102, 'Christine', 'Holand')")
        query.exec_("insert into person values(103, 'Lars', 'Gordon')")
        query.exec_("insert into person values(104, 'Roberto', 'Robitaille')")
        query.exec_("insert into person values(105, 'Maria', 'Papadopoulos')")
        
        query.exec_("select id, firstname from person")
        return query
    
    #query = setup_db_sqlite()
    
    
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

    
    
    query = QSqlQuery('''
            SELECT CONCAT(UC.nombre_uc, '(' ,UC.id_UC,')'), 
            UC.id FROM UC WHERE UC.co_id = %(co_id)d
        ''' % {'co_id':1})
    
    print "Error?", query.lastError().databaseText()
    model = QSqlQueryModel()

    model.setQuery(query)
    
    combo_box = QComboBoxModelQuery()
    combo_box.setMinimumWidth(400)
    
    def prueba(index):
        print "-------------------------------------------------------------"
        print index
        print "El id es", combo_box.get_col_value(0),\
            combo_box.get_col_value()
    
    print "Conexion", combo_box.connect(combo_box, SIGNAL('currentIndexChanged(int)'), prueba)
    combo_box.setWindowTitle("Texto")
    combo_box.setModel(model)
    combo_box.show()
    #combo_box.setModelColumn(1)
    qApp.exec_()