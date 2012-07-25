#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
La misión de este módulo es detectar paquetes validos bajo el protocolo
uCNet.
'''

import logging
import sys
import proto, checksum

#------------------------------------------------------------------------------ 
# Orden de bytes:
# Sof    Qty    Dst    Src    Sec    Com    Dato    BCCH    BCCL
#  0      1      2      3      4      5       6      7       8
#------------------------------------------------------------------------------

# Por referencia ciruclar, definimos los estados después de las funciones
ESTADOS = {}

def espera_sof(entrada, autom):
    ''' Espera SOF '''
    if entrada == proto.SOF:
        autom.buffer.append(entrada)
        return ESTADOS['ESPERA_QTY']
    autom.logger.debug('SOF :(')
    autom.logger.info('No se recibió comienzo de trama sino %d' % entrada)


def espera_qty(entrada, autom):
    ''' Espera QTY '''
    if entrada >= proto.MIN_QTY and entrada <= proto.MAX_QTY:
        autom.buffer.append(entrada)
        autom.long_actual = entrada
        autom.logger.info('QTY OK, %d %s' % (entrada, type(entrada)))
        return ESTADOS['ESPERA_SRC']
    # Descartamos el Buffer 
    autom.logger.info('Longitud de paquete incorrecta %d' % entrada)
    autom.buffer = []
    return ESTADOS['ESPERA_SOF']

def espera_src(entrada, autom):
    ''' Espera SRC '''
    autom.buffer.append(entrada)
    return ESTADOS['ESPERA_DST']

def espera_dst(entrada, autom):
    ''' Espera DST '''
    autom.buffer.append(entrada)
    return ESTADOS['ESPERA_SEC']

def espera_sec(entrada, autom):
    ''' Espera SEC 
    Como el autómata no tiene control sobre el reenvio de paquetes,
    deja que la capa superior (hilo del concentrador) se encargue[
    de revisar la secuencia.
    '''
    autom.buffer.append(entrada)
    return ESTADOS['ESPERA_COM']

def espera_com(entrada, autom):
    ''' Espera COM '''
    if entrada in proto.COMANDOS.values():
        autom.buffer.append(entrada)
        if autom.long_actual == proto.MIN_QTY:
            autom.logger.info('No hay datos')
            return ESTADOS['ESPERA_BCH']
        autom.logger.info('Cantidad de datos a recibir: %d' %
                          (autom.long_actual - len(autom.buffer)))
        return ESTADOS['ESPERA_DATO']

    autom.buffer = []
    return ESTADOS['ESPERA_SOF']


def espera_dato(entrada, autom):
    ''' Espera DATO '''
    autom.buffer.append(entrada)
    if (autom.long_actual - len(autom.buffer)) == 2:
        # Si me quedan dos, son BCH, BCL
        return ESTADOS['ESPERA_BCH'] 

def espera_bch(entrada, autom):
    ''' Espera BCH '''
    autom.buffer.append(entrada)
    return ESTADOS['ESPERA_BCL']

def espera_bcl(entrada, autom):
    ''' Espera BCL '''
    autom.buffer.append(entrada)
    
    autom.logger.info('Recibida totalidad de paquete')
    autom.logger.info('Checksum: ' + (checksum.check_cs_bigendian(autom.buffer) and "OK" or "Error"))
    if checksum.check_cs_bigendian(autom.buffer):
        autom.packet.append(autom.buffer)
        autom.buffer = []
    return ESTADOS['ESPERA_SOF']

ESTADOS.update({
           'ESPERA_SOF':    espera_sof,
           'ESPERA_QTY':    espera_qty,
           'ESPERA_SRC':    espera_src,
           'ESPERA_DST':    espera_dst,
           'ESPERA_SEC':    espera_sec,
           'ESPERA_COM':    espera_com,
           'ESPERA_DATO':   espera_dato,
           'ESPERA_BCH':    espera_bch,
           'ESPERA_BCL':    espera_bcl,
})


class UCNetPacketDetector(object):
    
    def __init__(self):
        # El buffer es de enetros
        self.buffer = []
        self.packet = []
        self.estado = ESTADOS['ESPERA_SOF']
        self.long_actual = 0
        self.logger = logging.getLogger('automata')
    
    def feed(self, entrada):
        ''' Alimentamos el autómata'''
        if not entrada:
            return
        for c in entrada:
            prox_est = self.estado(ord(c), self)
            # Si hay que cambiar de estado...
            if prox_est:
                self.estado = prox_est
    
    def ready(self):
        return False
    
    def get_pkg(self):
        return (self.packet and self.packet.pop() or None)
    
    def get_error(self):
        return None


def set_logger():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%d-%m-%y %H:%M',
                        filename='automata.log',
                        filemode='w')
    
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    
    
def main(argv = sys.argv):
    ''' Punto de entrada al programa'''
    
    set_logger()
    logger = logging.getLogger('automata')
    
    
    datos = [proto.SOF,   # Start of Frame 
             0,     # Quantity
             1,     # Origen
             2,     # Destino
             5,     # Secuencia
             0,     # Comando 0 (Peticion de estados y eventos)
             3,     # Cantidad de DI (Digital Input)        autom.logger.info('QTY OK, %d %s' % (entrada, type(entrada)))
             0x0C,  # PORTA
             0xfe,  # PORTB
             0xac,  # PORTC
             2,     # Cantidad de AI (Analog Input)
             0x03,  # AI0H  
             0xaa,  # AI0L
             0x03,  # AI1H
             0xaf,  # AI1L
             0,     # Cantidad de evntos (por ahora sin eventos, poruqe son de 7 bytes
             ]
    datos[1] = len(datos) + 2 # Preagregamos el checksum
    datos += make_cs_bigendian(datos) # Concatenamos el checksum
    logger.info(' '.join( [('%.2x' % i).upper() for i in datos]))
    datos_cadena = ''.join([chr(i) for i in datos])
    assert len(datos) == len(datos_cadena), "Error en la conversion de cadena"
    logger.info('Cadena: '+ datos_cadena)
    
    logger.warn('Creando automata de prueba')
    automata = UCNetPacketDetector()
    automata.feed(datos_cadena)
    return 0

if __name__ == "__main__":
    sys.exit(main())
