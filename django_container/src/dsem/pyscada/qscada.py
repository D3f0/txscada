#! /usr/bin/env python
# -*- encoding: utf-8 -*-


from PyQt4.QtCore import SIGNAL 
from PyQt4.QtGui import qApp
#from scada import PicnetSCADAProtocolFactory
from scada import PicnetSCADAProtocol, ScadaClientFacotry
from twisted.python import log


class PicnetSCADAProtocolQEvents(PicnetSCADAProtocol):
    '''
    Notificación de eventos a la GUI mediante la infraestructura de signals/slotsd
    de Qt.
    '''
    def notify_data(self, co, uc, svs, dis, ais, evs):
        '''
        Porpagación a travez de la aplicación de los datos para
        que las partes de la UI que necesiten refrescarse lo hagan
        tan pronto como puedan. De esta manera no es necesario 
        acceder a la base de datos.
        '''
        log.msg('Propagando datos a la GUI de COID: %.2d%.2d' % (co, uc))
        qApp.instance().emit(SIGNAL('data_available'), co, uc, svs, dis, ais, evs)
        
    def uc_state_change(self, co):
        log.msg('Propagando cambi en UCs de %d' % co)
        qApp.instance().emit(SIGNAL('uc_changed'), co)

    def packageRecieved(self, pkg):
        PicnetSCADAProtocol.packageRecieved(self, pkg)
        cadena = "%s\n" % pkg.hex_dump()
        qApp.instance().emit(SIGNAL('data_received'), cadena)
        
class ScadaClientFactoryQEvents(ScadaClientFacotry):
    ''' SCADA para el clinete'''
    protocol = PicnetSCADAProtocolQEvents
    
    def stopped(self):
        qApp.instance().win.actionStart.setChecked(False)
        qApp.instance().win.statusbar.showMessage('Scada detenido')
    
    def started(self):
        qApp.instance().win.statusbar.showMessage('Scada iniciado')
    
    