#! /usr/bin/env python
# -*- encoding: utf-8 -*-
 
from PyQt4.Qt import *

from ui_cfgserial import Ui_CfgSerialDialog
import sys
BROKEN = False

try:
    import serial
    
except ImportError, e:
    QMessageBox.information(None, u'Error en PySerial o PyWin32', 
    u'''No se encuentra el paquete win32 necesario para acceder al puerto serie<br/>
    Puede descargarse desde http://ufpr.dl.sourceforge.net/sourceforge/pywin32/pywin32-212.win32-py2.5.exe<br />
    PySerial se puede instalar mediante distutils (easy_install pyserial) o mediante
    la web:
    ''')
    BROKEN = True

PORTS = '''/dev/ttyS0 /dev/ttyS1 /dev/ttyS2 /dev/ttyS3 /dev/ttyUSB0 /dev/ttyUSB1
/dev/ttyUSB2 /dev/ttyUSB3 COM1 COM2 COM3 COM4 COM5 COM6 COM7 COM8'''.split()


def configQComboBox(combo, values, default = None):
    values = map(str, values)
    combo.addItems(values)
    if default and default in values:
        combo.setCurrentIndex( values.index(default) )

class CfgSerialDialog(Ui_CfgSerialDialog, QDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        # Rellenamos el diaogo con los datos que trae pyserial en vez de
        # presetendolos en la GUI
        configQComboBox(self.comboPort, self.guess_serial_ports())
        configQComboBox(self.comboSpeed, serial.Serial.BAUDRATES, '9600')
        configQComboBox(self.comboSize, serial.Serial.BYTESIZES, '8')
        configQComboBox(self.comboParity, serial.Serial.PARITIES, 'N')
        configQComboBox(self.comboStop, serial.Serial.STOPBITS, '1')
        configQComboBox(self.comboXonXoff, [0,1], '0')
        configQComboBox(self.comboRtsCts, [0, 1], '0')
        configQComboBox(self.comboDsrDtr, [0, 1], '0')
        
    def guess_serial_ports(self):
        ports = []
        for port in PORTS:
            try:
                s = serial.Serial(port)
            except serial.SerialException, e:
                pass
            else:
                ports.append(port)
        return ports



    def get_config(self):
        ''' Retorna el diccionario de configuacion '''
        timeout = self.spinTimeOut.value()
        if timeout < 0:
            timeout = None
        return {
            'port' : str(self.comboPort.currentText()),
            'baudrate' : int(self.comboSpeed.currentText()),
            'bytesize' : int(self.comboSize.currentText()),
            'parity' : str(self.comboParity.currentText()),
            'stopbits' : int(self.comboStop.currentText()),
            'timeout' : timeout,
            #enable software flow control
            'xonxoff' : int(self.comboXonXoff.currentText()), 
            #enable RTS/CTS flow control
            'rtscts' : int(self.comboRtsCts.currentText()),
            #Inter-character timeout, None to disable
            # 'interCharTimeout' : None,
        }

