#! /usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Aplicación gráfica que genera encuesta a los semáforos.
'''

import sys
sys.path += ['..', '../..']

import psyco
import sip
from gui.twisted_app import QTwistedApp
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui.basewidget import QBaseWidget
from picnet.bitfield import bitfield
from pyscada.gui.customwidgets import QLogger

class Semaforo(QGraphicsItem):
    '''
    Clase para el semaforo.
    '''
    WIDTH, HEIGHT = 48, 136
    BASE_COLOR      = QColor(0x33, 0x4a, 0x4a)
    # On
    GREEN_COLOR_ON  = QColor.fromHsv(121, 230, 254)
    YELLOW_COLOR_ON = QColor.fromHsv(63, 226, 245)
    RED_COLOR_ON    = QColor.fromHsv(0, 226, 245)
    # Off
    GREEN_COLOR_OFF = QColor.fromHsv(121, 230, 64)
    YELLOW_COLOR_OFF= QColor.fromHsv(63, 226, 64)
    RED_COLOR_OFF   = QColor.fromHsv(0, 226, 48)
    
    BoundingRect = QRectF(0,0, WIDTH, HEIGHT)
    
    # Este arreglo se indexa por los los bits 
    COLOR_BIT_MAPPING = (
        (GREEN_COLOR_ON, YELLOW_COLOR_OFF, RED_COLOR_OFF, ), # 00
        (GREEN_COLOR_OFF, YELLOW_COLOR_OFF, RED_COLOR_ON, ), # 01 
        (GREEN_COLOR_OFF, YELLOW_COLOR_ON, RED_COLOR_OFF, ), # 10
        (GREEN_COLOR_OFF, YELLOW_COLOR_ON, RED_COLOR_ON, ),  # 11
    )
    
    def __init__(self, x, y):
        '''
        Constructor
        @param x: Posicion horizontal sobre la escena
        @param y: Posicion vertical sobre la escena
        '''
        QGraphicsItem.__init__(self)
        self.setPos(x, y)
        
        self.bit_update(0)
        
        #TODO: Ver si no está muy acoplado
        self.n_uc = 0
        self.n_port = 0
        self.n_bit = 0
    
    def paint(self, painter, options, widget):
        ''' Dibuja el semáforo '''
        painter.setPen(self.BASE_COLOR)
        painter.setBrush(QBrush(self.BASE_COLOR))
        # Dibujamos la figura de semáforo
        painter.drawPath(self.shape())
        
        painter.setPen(QColor(0xff, 0xff, 0xff))
        painter.setBrush(self.red)
        painter.drawEllipse(2,4,44,44)
        painter.setBrush(self.yellow)
        painter.drawEllipse(7,52,35,36)
        painter.setBrush(self.green)
        painter.drawEllipse(7,92,35,36)
        
    def boundingRect(self):
        ''' Retrona el area para el redibujado '''
        return self.BoundingRect
    
    def shape(self):
        ''' Retorna la forma activa '''
        p = QPainterPath()
        p.addRoundedRect(self.boundingRect(), 5.0,5.0)
        return p
    
    #def shape(self):
    def bit_update(self, bits):
        ''' Actualiza la GUI en funcion de los bits '''
        assert bits >= 0 and bits < 4, "Bits incorrectos"
        self.green, self.yellow, self.red = self.COLOR_BIT_MAPPING[bits] 
        self.update()
    
    def di_data_slot(self, n_uc, dis):
        #from twisted.python import log
        if n_uc == self.n_uc:
            #self.bit_update()
            port = bitfield(dis[self.n_port])
            
            bits = port[self.n_bit: self.n_bit +2] 
            self.bit_update(bits)
            #log.msg("Actualizando con %s" % bits)
            
        



def main(argv = sys.argv):
    # Lanzamos la aplicacion
    app = QTwistedApp(argv)
    from twisted.internet import reactor
    sems = []
    win = QBaseWidget()
    layout = QVBoxLayout()
    win.setLayout(layout)
    escena = QGraphicsScene(0,0,400,400)
    visor = QGraphicsView()
    visor.setScene(escena)
    visor.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    #visor.setMinimumSize(400,400)
    layout.addWidget(visor)
    
    visor.setRenderHint(QPainter.Antialiasing)
            # UC, Port, Bit
    movis = ((2,1,0), 
             (2,1,2),
             (3,1,0),
             (3,1,2),
             
             (4,1,0),
             (4,1,2),
             
             )
    
    
    for n in xrange(6):
        s = Semaforo(56 * n + 30, 20)
        s.setToolTip(u"Movimiento N° %d" % (n+1))
        escena.addItem(s)
        s.n_uc, s.n_port, s.n_bit = movis[n]
        
        sems.append(s)
        
        
    b = QPushButton('Show log')
    b.setCheckable(True)
    layout.addWidget(b)
    t = QTextEdit()
    logger = QLogger()
    logger.connect(logger, SIGNAL('flush(QString)'), t.append)
    from twisted.python import log
    log.startLogging(logger, setStdout = False)
    #t.setEnabled(False)
    t.setReadOnly(True)
    layout.addWidget(t)
    t.hide()
    def button_pressed(checked):
        if checked:
            t.show()
        else:
            t.hide()
    b.connect(b, SIGNAL('toggled(bool)'), button_pressed)
    QObject.connect(qApp, SIGNAL('lastWindowClosed ()'),
                           reactor.stop)
    
    #log.startLogging(sys.stdout, setStdout = False)
    
    from pyscada.scada import SCADAEngine
    from pyscada.model import metadata
    
    from scada import PicnetSCADAProtocolFactory
    # Creamos una instancia de Scada
    scada = SCADAEngine()
    #scada.factory = QClientFactory
    #scada.factory = PicnetSCADAProtocolFactory
    # Puerto TCP 
    scada.tcp_port = 9761
    # Descripcion de la base de datos
    scada.metadata = metadata
    # Verborragia minima
    scada.verbosity = 1
    # El concentrador tiene DI = 1
    scada.id_rs485 = 1
    
    scada.db_engine = 'mysql://dsem:passmenot@localhost:3306/dsem'
    log.msg("Inicnando scada", scada)
    
    #from extra_hmi_test import conectar
    
    def conectar( cfs ):
        # Esto es muy chancho, taomamos el primer concentrador
        c0 = cfs[ cfs.keys()[0]]
        # Y a todo el arrglo de semáforos lo conectamos con las señales que
        # genere el ClientFactory
        for s in sems:
            QObject.connect(c0, SIGNAL('di_data_received'), s.di_data_slot )
        
        log.msg('Conexion de semaforos OK')
        
    scada.connection_defer.addCallback(conectar)
        
    #escena.addWidget(b)
    # Cuando se cierra la ventana se cierra el SCADA
    QObject.connect(win, SIGNAL('closed()'), reactor.stop)
    # Mostrar la ventana
    win.show()
    # Arrancar el scada
    scada.start()
    # Correr el reactor
    reactor.run()
    

if __name__ == '__main__':
    main()

