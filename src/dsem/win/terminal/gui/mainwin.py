#! /usr/bin/env python
# -*- encoding: utf-8 -*-
 
import os
import sys
from PyQt4 import QtCore, QtGui

from ui_mainwin import Ui_Form
from aboutwin import AboutDialog
from cfgsocket import SocketCfgDialog
from cfgserial import CfgSerialDialog
from socket import socket, SHUT_RD, SHUT_WR, SHUT_RDWR, error
from picnet.dtime import DTime
import serial

try:
    from picnet.proto import Paquete
except ImportError, e:
    sys.stdout.write('''No se puede importar el modulo de Paquete. 
    Comprube que dascada se encuentre en su path.''')

DATA_LENGTH = 255


def str2hexa(data):
    data = ' '.join([ '%.2x' % ord(x) for x in str(data)])
    return data.upper()

def hexa2str(data):
    return ''.join([ chr(int(chunk, 16)) for chunk in data.split() if chunk])

#TODO: Generalizar las funciones de las clases hilo

class SocketThread(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)
        # Recibe de la GUI las señales de connect y disconnect
        self.connect(parent, QtCore.SIGNAL('do_connect'), self.do_connect )
        self.connect(parent, QtCore.SIGNAL('do_disconnect'), self.do_disconnect)
        self.connect(QtGui.qApp, QtCore.SIGNAL('aboutToQuit()'), self.cerrar)
        self.addr, self.timeout = None, None
        self.socket = socket()
        self.do_close = False
        
    def do_connect(self, addr, timeout):
        self.addr, self.timeout = addr, timeout
        self.do_close = False
        self.start()
        
    def do_disconnect(self):
        # Setea la bandera
        self.do_close = True

    def run(self):
        # El timeout para el connect
        self.socket.settimeout(2.0)
        try:
            self.socket.connect(self.addr)
        except error, e:
            # Si hay problemas al conectar
            self.emit(QtCore.SIGNAL('socket_error'), e)
            self.socket.shutdown(SHUT_RD)
            # Terminamos el hilo, no hay nada que hacer
            return
        else:
            self.emit(QtCore.SIGNAL('socket_connected'))
        
        # Volvemos bloqueante al socket
        self.socket.settimeout(self.timeout)
        
        while True:
            try:
                data = self.socket.recv(DATA_LENGTH)
                if not data:
                    if self.do_close:
                        print "socket.close()"
                        self.socket.shutdown(SHUT_RDWR)
                        self.socket.close()
                        return
            except error, e:
                # Como pusimos el socket con timeout...
                if self.socket.gettimeout():
                    continue
                # pero si el error es otro...
                self.emit(QtCore.SIGNAL('socket_error'), e)
                return
            else:
                self.emit(QtCore.SIGNAL('socket_received'), data)
                print "SOCKET <- %s %d" % (str2hexa(data), len(data))
    
    def cerrar(self):
        # print "Salida"
        try:
            self.socket.shutdown(SHUT_RDWR)
            self.socket.close()
        except Exception, e:
            pass
        
    def send(self, data):
        ''' Envia los datos por el socket '''
        print "SOCKET -> %s %d" % (str2hexa(data), len(data))  
        self.socket.send(data)
    
class SerialThread(QtCore.QThread):
    '''
    El hilo encargado del manejo del puerto serial
    '''
    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)
        self.serial = None
        self.do_close = False
        # Señales de la GUI
        self.connect(parent, QtCore.SIGNAL('do_connect_serial'), 
                                                    self.handle_serial_connect)
        self.connect(parent, QtCore.SIGNAL('do_disconnect_serial'), 
                                                self.handle_serial_disconnect)
                                                
    def handle_serial_connect(self, conf):
        
        try:
            self.serial = serial.Serial(**conf)
            self.serial.open()
        except serial.SerialException, e:
            self.emit(QtCore.SIGNAL('serial_error'), e)
        else:
            self.do_close = False
            self.emit(QtCore.SIGNAL('serial_connect'))
        
        self.start()
        
    def run(self):
        self.serial.setTimeout(0.02)    # Escaneo cada 20 mS
        while True:
            try:
                data = self.serial.read(DATA_LENGTH)
                if data:
                    print "SERIAL <- %s %d" % (str2hexa(data), len(data))
                    self.emit(QtCore.SIGNAL('serial_received'), data )
                else:
                    if self.do_close:
                        print "Finalizando hilo serial"
                        return
                    
            except serial.SerialException, e:
                self.emit(QtCore.SIGNAL('serial_error'), e)
                return
                
    def handle_serial_disconnect(self):
        self.do_close = True
    
    def send(self, data):
        ''' Enviar datos al puerto serie '''
        print "SERIAL -> %s %d" % (str2hexa(data), len(data))
        try:
            self.serial.write(data)
        except serial.SerialException, e:
            print "Error en el envio", e


class PeriodicRequestThread(QtCore.QThread):
    def __init__(self, parent, paquete, name, start_now = False):
        signal_start = 'start_%s' % name
        signal_stop = 'stop_%s' % name
        signal_set_interval = 'set_interval_%s' % name
        self.connect(parent, QtCore.SIGNAL(signal_start), self.do_start)
        self.connect(parent, QtCore.SIGNAL(signal_stop), self.do_stop)
        self.connect(parent, QtCore.SIGNAL(signal_set_interval), self.set_interval)
        
        self.start_now = start_now
        if self.start_now:
            self.start()
    
    def set_interval(self, interval):
        pass
        
    def run(self):
        pass
    
    def do_start(self):
        pass
    
    def do_stop(self):
        pass

    
class MainWin(Ui_Form, QtGui.QWidget):
    '''
    Ventana principal del programa
    '''
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.validador_hex = QtGui.QRegExpValidator(QtCore.QRegExp("([abcdefABCDEF\\d]{1,2}\\s)*"), self)
        # Inicializamos la entrada como entrada HEXA
        self.entrada_hexa()
        self.cfgsocket_dlg = SocketCfgDialog()
        # Hilo para atencion del socket
        self.socket_thread = SocketThread(self)
        self.connect(self.socket_thread, QtCore.SIGNAL('socket_error'), self.handle_socket_error)
        self.connect(self.socket_thread, QtCore.SIGNAL('socket_connected'), self.handle_socket_connected)
        self.connect(self.socket_thread, QtCore.SIGNAL('socket_received'), self.handle_received)
        # Estado privado
        self.__socket_conectado = False
        self.__serial_conectado = False
        
        # self.socket_conectado = True
        
        # Configuración del puerto serie
        self.cfgserial_dlg = CfgSerialDialog()
        self.serial_thread = SerialThread(self)
        self.connect(self.serial_thread, QtCore.SIGNAL('serial_error'), self.handle_serial_error)
        self.connect(self.serial_thread, QtCore.SIGNAL('serial_connect'), self.handle_serial_connect)
        self.connect(self.serial_thread, QtCore.SIGNAL('serial_received'), self.handle_received)
        # String de aplicacion
        self.lineAppString.setValidator(self.validador_hex)
        self.lineMemoryData.setValidator(self.validador_hex)
        
        # Rango de microcontroladores
        self.lineDirRange.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r'^[(\d{1,3})(\d{1,3}\-\d{1,3})\s]*$'),self))
        
        self.connect(self, QtCore.SIGNAL('send'), self.handle_send)
        
        
    def set_socket_conectado(self, estado):
        ''' Setter '''
        self.__socket_conectado = estado
        if estado:
            self.check_envio_socket.setEnabled(True)
            self.pushConnect_socket.setText('Desconectar')
            self.label_status_socket.setText('Conectado')
        else:
            self.check_envio_socket.setEnabled(False)
            self.pushConnect_socket.setText('Conectar')
            self.label_status_socket.setText('Desconectado')
    
    def get_socket_conectado(self):
        ''' Getter '''
        return self.__socket_conectado
        
    def set_serial_conectado(self, estado):
        ''' Setter '''
        self.__serial_conectado = estado
        if estado:
            self.check_envio_serial.setEnabled(True)
            self.pushConnect_serial.setText('Desconectar')
            self.labelConexionSerial.setText('Conectado')
        else:
            self.check_envio_serial.setEnabled(False)
            self.pushConnect_serial.setText('Conectar')
            self.labelConexionSerial.setText('Desconectado')
    
    def get_serial_conectado(self):
        ''' Getter '''
        return self.__serial_conectado
    
    socket_conectado = property(get_socket_conectado, set_socket_conectado)
    serial_conectado = property(get_serial_conectado, set_serial_conectado)
        
    @QtCore.pyqtSignature('QString')
    def on_combo_modo_currentIndexChanged(self, modo):
        ''' Cambio del modo en el que se interpreta la lina de entrada '''
        modo = str(modo).lower() # De QString a str de python
        texto = str(self.line_envio.text())
        
        if modo == 'hexadecimal':
            self.entrada_hexa()
            # Pasamos el contenido a hexa
            self.line_envio.setText(str2hexa(texto))
            
        elif modo == 'ascii':
            self.entrada_ascii()
            # Pasamos el contenido a Hexa
            self.line_envio.setText(hexa2str(texto))
            
        self.line_envio.setFocus()
            
    def entrada_hexa(self):
        ''' Establece la entrada como HEXADECIMAL'''
        self.line_envio.setValidator(self.validador_hex)
        self.line_envio.setToolTip('Aceptando solo entrada Hexadecimal')
        
    def entrada_ascii(self):
        ''' Establece la entrada como ASCII'''
        self.line_envio.setValidator(None)
        self.line_envio.setToolTip('Aceptando entrada ASCII')
    
    def on_push_about_pressed(self):
        if not hasattr(self, 'about_dlg'):
            self.about_dlg = AboutDialog()
        self.about_dlg.exec_()
        
    def on_pushConf_socket_pressed(self):
        val = self.cfgsocket_dlg.exec_()
        
    def on_pushConnect_socket_pressed(self):
        if not self.socket_conectado:
            self.emit(QtCore.SIGNAL('do_connect'), self.cfgsocket_dlg.get_addr(), 
                        self.cfgsocket_dlg.get_timeout())
            self.pushConnect_socket.setText('Conectando...')
        else:
            self.emit(QtCore.SIGNAL('do_disconnect'))
            self.socket_conectado = False
        
    def handle_socket_error(self, e):
        print "Error de socket:", e
        self.socket_conectado = False
    
    def handle_socket_connected(self):
        self.socket_conectado = True
        
    def handle_received(self, data):
        ''' Recibir datos '''
        if self.check_del_slashn.isChecked():
            data = data.rstrip('\n')
        if self.check_recv_hexa.isChecked():
            data = str2hexa(data)
        self.textReceived.appendPlainText(data)
    
    def on_pushConf_serial_pressed(self):
        val = self.cfgserial_dlg.exec_()
        print self.cfgserial_dlg.get_config()
        
    def on_pushConnect_serial_pressed(self):
        if not self.serial_conectado:
            self.emit(QtCore.SIGNAL("do_connect_serial"), self.cfgserial_dlg.get_config())
        else:
            self.emit(QtCore.SIGNAL("do_disconnect_serial"))
            self.serial_conectado = False
            
    def handle_serial_connect(self):
        self.serial_conectado = True
        print "Serial conectado"
        
    def handle_serial_error(self, error):
        pass
    
    def on_pushEnviar_pressed(self):
        '''
        Envio de la cadena
        '''
        cadena = str(self.line_envio.text())
        if not cadena:
            return
        print "Serial, Socket:", self.serial_conectado, self.socket_conectado
        if not self.serial_conectado and not self.socket_conectado:
            QtGui.QMessageBox.information(self, 'No se puede enviar', '''
                Para poder enviar conectese mediante un socket o por RS232
            ''')
            return
        if not self.check_envio_socket.isChecked() and not \
            self.check_envio_serial.isChecked():
            QtGui.QMessageBox.information(self, 'No se puede enviar', '''
                Habilite al menos una forma de envio
            ''')
            return
        
        if str(self.combo_modo.currentText()).lower().count('hexa'):
            cadena = hexa2str(cadena)
        print "Envio"
        self.emit(QtCore.SIGNAL('send'), cadena)
            
    def on_check_envio_serial_stateChanged(self, state):
        ''' Envio sobre serial '''
        if state == QtCore.Qt.Checked:
            self.connect(self, QtCore.SIGNAL('send'), self.serial_thread.send)
        else:
            self.disconnect(self, QtCore.SIGNAL('send'), self.serial_thread.send)
    
    def on_check_envio_socket_stateChanged(self, state):
        ''' Envio sobre socket '''
        if state == QtCore.Qt.Checked:
            self.connect(self, QtCore.SIGNAL('send'), self.socket_thread.send)
        else:
            self.disconnect(self, QtCore.SIGNAL('send'), self.socket_thread.send)
    
    def handle_send(self, data):
        if self.check_send_hexa.isChecked():
            data = str2hexa(data)
        self.textEnvio.appendPlainText(data)
    
    # Getters y setters para secuencia
    
    def get_secuencia(self):
        ''' Maneja el numero de secuencia '''
        prev = val = self.spinSecuencia.value()
        val += 1
        if val > self.spinSecuencia.maximum():
            val = self.spinSecuencia.minimum()
        self.spinSecuencia.setValue(val)
        return prev
        
    def set_secuencia(self, valor):
        self.spinSecuencia.setValue(valor)
    
    # Propiedad para la secuencia
    secuencia = property(get_secuencia, set_secuencia)
    
    def get_orgien(self):
        return self.spinOrigen.value()
    
    def set_origen(self, valor):
        self.spinOrigen.setValue(valor)
    
    origen = property(get_orgien, set_origen)
    
    def get_destino(self):
        return self.spinDestino.value()
    
    def set_destino(self, valor):
        self.spinDestino.setValue(valor)
    
    destino = property(get_destino, set_destino)
    
    # Manejo de los botones de enviar comando
    def on_pushSendReqEv_pressed(self):
        pkg = Paquete.crear_estados_y_eventos(self.origen, self.destino, 
                                                self.secuencia)
        self.entrada_hexa()
        self.line_envio.setText(pkg.hex_dump())
    
    def on_pushSendReqMorEv_pressed(self):
        pkg = Paquete.crear_mas_eventos(self.origen, self.destino, 
                                            self.secuencia)
        self.entrada_hexa()
        self.line_envio.setText(pkg.hex_dump())
        
    def on_pushControl_pressed(self):
        puerto = self.spinPuerto.value()
        bit = self.spinBit.value()
        estado = self.radioBitUno.isChecked() and 1 or 0
        indirecto = self.checkIndirecto.isChecked()
        pkg = Paquete.crear_control(self.origen, self.destino, self.secuencia, 
                                    puerto, bit, estado, 
                                    es_comando_indirecto = indirecto)
        self.entrada_hexa()
        self.line_envio.setText(pkg.hex_dump())
    
    def on_pushLeerRam_pressed(self):
        pagina = self.spinPagina.value()
        direccion = self.spinDireccion.value()
        cantidad = self.spinCantidad.value()
        pkg = Paquete.crear_lectura_ram(self.origen, self.destino, self.secuencia, 
                                        pagina, direccion, cantidad)
        self.entrada_hexa()
        self.line_envio.setText(pkg.hex_dump())
        
    def on_pushLeerEE_pressed(self):
        pagina = self.spinPagina.value()
        direccion = self.spinDireccion.value()
        cantidad = self.spinCantidad.value()
        pkg = Paquete.crear_lectura_eeprom(self.origen, self.destino, self.secuencia, 
                                        pagina, direccion, cantidad)
        self.entrada_hexa()
        self.line_envio.setText(pkg.hex_dump())
    
    def on_pushPuestaEnHora_pressed(self):
        #QtGui.QMessageBox.information(self, 'hola', 'Hola')
        pkg = Paquete.crear_puesta_en_hora(self.origen, self.destino, 
                                           self.secuencia)
        self.entrada_hexa()
        self.line_envio.setText(pkg.hex_dump())
    
    def on_pushEnviarAppString_pressed(self):
        lista = [ int(x, 16) for x in str(self.lineAppString.text()).split() if len(x)]
        pkg = Paquete.crear_paquete_custom(self.origen, self.destino, 
                                           self.secuencia, lista)
        self.entrada_hexa()
        self.line_envio.setText(pkg.hex_dump())
    
    #@QtCore.pyqtSignature('int')
    def on_checkRequerirEstados_stateChanged(self, state):
        if state == QtCore.Qt.Checked:
            print "Requerir estados"
        else:
            print "No requerir mas eventos"
    
    def on_checkRequerirEventos_stateChanged(self, state):
        if state == QtCore.Qt.Checked:
            print "Requerir eventos"
        else:
            print "No requerir mas eventos"
        
    #TODO: Implementar esto    
    def on_pushHex2Bin_pressed(self):
        valor, ok = QtGui.QInputDialog.getText(self, "Ingrese un entero", "Entro a convertir")
        try:
            pass
        except:
            pass
    