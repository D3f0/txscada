#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from twisted.internet.defer import Deferred

import sys
if not hasattr(sys, 'frozen') and __name__ == "__main__":
    sys.path += ('..', '../..', '../../..')
from pyscada.gui.ui_print_dlg import Ui_PrintDialog
from pyscada.gui.qt_dbhelp import PyQSqlQuery
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtSql
from PyQt4.QtGui import QDialog, QMessageBox, QDialogButtonBox
from PyQt4.QtCore import QDate, pyqtSignature, QVariant 
from PyQt4.QtSql import *
from twisted.python import log
from jinja2 import Template
import cStringIO as StringIO
from tempfile import mktemp
from ho import pisa
import os
import commands
from time import time
from dateutil.relativedelta import relativedelta
from datetime import date
from config import Config
from optparse import OptionParser
from twisted.internet import threads

#
# Definicion de las querys
#
 
QUERY_ALL_CO = """
    SELECT CONCAT(COALESCE(CO.nombre_co, 'CO'), ' - (', COALESCE(ip_address, 'Sin IP'), ')'), id_CO FROM CO
""".strip()

QUERY_UC_FOR_CO = """
    SELECT CONCAT(COALESCE(nombre_uc, 'UC'),' ', id_UC), id FROM UC WHERE UC.co_id = %d
""".strip()

MYSQL_DATE_FORMAT_FOR_QSTRING = 'yyyy-M-d hh:mm:00'


def guardar_reporte(html):
    '''
    Guarar el template
    '''
    nombre_salida = mktemp('.pdf', 'reporte-')
    log.msg('Generando reporte con el nombre %s' % nombre_salida)
    salida_archivo = open(nombre_salida, 'w')
    pdf = pisa.pisaDocument(html.encode("UTF-8"), salida_archivo)
    
    
    salida_archivo.close()
    if not pdf:
        raise Exception('No se pudo generar el pdf')
    else:
        log.msg('Trying to open report')
        if sys.platform.count('linux'):
            cmd = commands.getoutput('which xdg-open')
            if cmd:
                os.spawnl(os.P_NOWAIT, cmd, cmd, nombre_salida)
            else:
                log.err('No puedo abrir el archivo %s' % nombre_salida)
        elif sys.platform.count('win32'):
            cmd = os.path.join(os.environ['WINDIR'], 'system32', 'cmd.exe')
            os.spawnl(os.P_NOWAIT, cmd, cmd, 'start', '/c', nombre_salida)
    

def render_template(var, template = None, query = None, fecha_desde = None, fecha_hasta = None):
    '''
    Renderizar el template, esta es la tarea más pesada.
    '''
    f = open(template, 'r')
    template = Template(f.read())
    f.close()
    #time2 = time()
    #log.msg("Lectura de template:\t%f" % (time2 - time1))
    salida_template = template.render(eventos = query,
                                      fecha_desde = fecha_desde.toPyDateTime(),
                                      fecha_hasta = fecha_hasta.toPyDateTime(),)
    
    threads.deferToThread(guardar_reporte, salida_template)


def mostar_excepcion(exc):
    QMessageBox.critical(None, "Error", "Se produjo el siguiente error %s" % exc)
    raise exc
 
class PrintDialog(Ui_PrintDialog, QDialog):
    
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        # Inicializacion de fechas
        hasta = date.today()
        desde = hasta - relativedelta(months = 1)
        self.dateTimeEdit_desde.setDate(QDate(desde.year, desde.month, desde.day))
        self.dateTimeEdit_hasta.setDate(QDate(hasta.year, hasta.month, hasta.day))
        
        self.model_co = QSqlQueryModel(self)
        self.model_uc = QSqlQueryModel(self)
        self.comboBox_CO.setModel(self.model_co)
        self.comboBox_UC.setModel(self.model_uc)
        self.model_co.setQuery(QUERY_ALL_CO)
        
        for i in range(0, 4):
            self.comboBox_tipo.addItem("Tipo %d" % i, QVariant(i))
            
        self._template = None
        
        if self.comboBox_CO.model().query().size() == 0:
            # Si no hay concentradores no se pueden imprimir reportes
            self.comboBox_CO.setEnabled(False)
            self.comboBox_UC.setEnabled(False)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        
        
        
    def template(): #@NoSelf
        doc = """Archivo de template para la generación de reportes""" #@UnusedVariable
       
        def fget(self):
            return self._template
           
        def fset(self, value):
            if not os.path.exists(value):
                raise IOError('El archivo de templates %s no existe' % value)
            self._template = value
        return locals()
       
    template = property(**template())
        
    @pyqtSignature('int')
    def on_comboBox_CO_currentIndexChanged(self, id):
        co_id = self.comboBox_CO.get_col_value()
        self.model_uc.setQuery(QUERY_UC_FOR_CO % co_id)
        result = self.model_uc.query().size() > 0
        self.comboBox_UC.setEnabled(result)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(result)
            
        
    @pyqtSignature('bool')
    def on_checkBox_todo_CO_clicked(self, clicked):
        # Todos los CO involucra todas las UC
        if not self.checkBox_todo_UC.isChecked():
            #self.checkBox_todo_UC.click()
            self.checkBox_todo_UC.setChecked(True)
        
    
    @pyqtSignature('bool')
    def on_checkBox_todo_UC_clicked(self, clicked):
        pass
    
    def exec_(self):
        return QDialog.exec_(self)
    
    def accept(self):
        ''' Generar la query en función del los parámetros '''
        where = ''
        # Filro por UC
        if self.comboBox_UC.isEnabled():
            where = 'EV.uc_id = %d' % self.comboBox_UC.get_col_value(1)
            
        # Filtro por tipo
        if self.comboBox_tipo.isEnabled():
            data = self.comboBox_tipo.itemData(self.comboBox_tipo.currentIndex())
            data = data.toInt()[0]
            if where:
                where = '%s AND EV.tipo = %s' % (where, data) 
            else:
                where = 'EV.tipo = %s' % (data, )
            
        fecha_desde = self.dateTimeEdit_desde.dateTime()
        fecha_hasta = self.dateTimeEdit_hasta.dateTime()
        where = where and '%s AND' % where
        
        query = PyQSqlQuery("""
            SELECT * FROM ((EV INNER JOIN UC ON EV.uc_id = UC.id)
            INNER JOIN CO ON UC.co_id = CO.id_CO) LEFT JOIN EV_Descripcion ON EV.tipo = EV_Descripcion.tipo 
                    AND EV.codigo = EV_Descripcion.codigo WHERE %s ts_bit >= '%s' AND ts_bit < '%s'
                    ORDER BY EV.ts_bit DESC, EV.ts_bit_ms DESC
                    """ %
                      (where, 
                       fecha_desde.toString(MYSQL_DATE_FORMAT_FOR_QSTRING), 
                       fecha_hasta.toString(MYSQL_DATE_FORMAT_FOR_QSTRING),
                       
                       )
            )
        
        query.exec_()
        
        if query.lastError().type() != QSqlError.NoError:
            log.msg('Error en la DB?: %s' %query.lastError().databaseText())
            QMessageBox.critical(self, "Error",
                                 '<p>Se ha producido un error «%s».</p>' % query.lastError().databaseText())
            return
        
        if not query.size():
            QMessageBox.information(self, "Sin resultados",
                                 '<p>La consulta no ha producido resultados.</p>')
            return
        d = Deferred()
        d.addCallback(render_template, template = self.template, 
                      query = query, 
                      fecha_desde = fecha_desde, 
                      fecha_hasta = fecha_hasta)
        d.addErrback(mostar_excepcion)
        d.callback(None)
        
#        try:
#            time1 = time()
#            f = open(self.template, 'r')
#            template = Template(f.read())
#            f.close()
#            time2 = time()
#            log.msg("Lectura de template:\t%f" % (time2 - time1))
#            salida_template = template.render(eventos = query,
#                                              fecha_desde = fecha_desde.toPyDateTime(),
#                                              fecha_hasta = fecha_hasta.toPyDateTime(),)
#            time3 = time()
#            log.msg("Renderizacion del template:\t%f" % (time3 - time2))
#            nombre_salida = mktemp('.pdf', 'reporte-')
#            salida_archivo = open(nombre_salida, 'w')
#            pdf = pisa.pisaDocument(salida_template.encode("UTF-8"), salida_archivo)
#            time4 = time()
#            log.msg("Generacion del documento:\t%f"%( time4 - time3))
#            if not pdf:
#                raise Exception('No se pudo generar el pdf')
#            salida_archivo.close()
#        except Exception, e:
#            import traceback
#            log.msg(traceback.format_exc())
#            QMessageBox.critical(self, u"Error",
#                                 u'<p>Se ha producido un error al generar el reporte «%s».</p>' % e)
#            log.err('Error %s' % e)
#            #raise
#        else:
#            log.msg('Trying to open report')
#            if sys.platform.count('linux'):
#                cmd = commands.getoutput('which xdg-open')
#                if cmd:
#                    os.spawnl(os.P_NOWAIT, cmd, cmd, nombre_salida)
#                else:
#                    log.err('No puedo abrir el archivo %s' % nombre_salida)
#            elif sys.platform.count('win32'):
#                cmd = os.path.join(os.environ['WINDIR'], 'system32', 'cmd.exe')
#                os.spawnl(os.P_NOWAIT, cmd, cmd, 'start', '/c', nombre_salida)
#                
        QDialog.accept(self)
    
    
    
    
def main(argv = sys.argv[1:]):
    #usage, option_list, option_class, version, conflict_handler, description, formatter, add_help_option, prog, epilog)
    parser = OptionParser(version = '%prog 0.0.1b',
                          description= u'''
                              Generador de reportes
                              Generador de reportes del sistema de semaforizacion Avrak.
                              El rpoerte es generado en PDF en un archivo temporal y este
                              debe ser guardado o impreso. El sistema operativo se deshará
                              del archivo si este no es guardado.
                          ''',
                          prog="print_dlg",
                          epilog = u"""Este software se encuentra bajo la licencia GPL v.3
                          Nahuel Defossé © 2009""")
    parser.add_option('-c', '--config',
                      default = '../config.cfg',
                      type=str,
                      help = "Archivo de configuracion",
                      dest = "config_file")
    opts, args = parser.parse_args(argv)
                          
    cfg = Config(opts.config_file)
    
    
    from PyQt4.QtGui import QApplication
    QApplication(argv)
    from pyscada.gui.qt_dbhelp import dburl_to_qsqldb
    log.startLogging(sys.stdout, setStdout = False)
    #db = dburl_to_qsqldb('mysql://dsem:passmenot@localhost:3306/dsem')
    
    db = dburl_to_qsqldb(**dict(cfg.scada))
    log.msg("DB OK? %s" % db.isValid())
    win = PrintDialog()
    win.template = '../templates/report.html'
    win.exec_()
    
if __name__ == "__main__":
    sys.exit(main())
    
    