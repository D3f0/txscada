#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
    Emulador del concentrador:
         La funcion de este modulo es emular el funcionamiento de un consentrador
         para realizar pruebas del scada.
"""
import socket
from threading import Thread
import sys
import atexit
from optparse import OptionParser
import logging
from picnet.proto import Paquete,SOF
from picnet.checksum import make_cs_bigendian

def set_logger():
    ''' Setea el logger '''
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%d-%m-%y %H:%M',
                        filename='emu_con.log',
                        filemode='w')
    
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
        
def main():
    set_logger()
    logger = logging.getLogger('emu_con')
    
    parser = OptionParser(description="Emulador de consentrador")
    parser.add_option("-p", "--port", dest="port", type=int, help="Puerto a conectarse")
    parser.add_option("-i", "--ip", dest="ip", type=str, help="Ip del concentrador")
    (options, args) = parser.parse_args(sys.argv)
    
    if not options.port:
        print "Debe especificar el puerto, para mas informacion utilize el parametro -h"
        sys.exit()
    if not options.ip:
        print "Debe especificar la IP del concentrador, para más inforamción utilize el parámetro -h"
        sys.exit()
    print options
    
    sock = socket.socket()
    logger.info("Espera coneccion en la ip %s, puerto %d" % (options.ip, options.port))
    sock.bind((options.ip, options.port))
    sock.listen(1)
    try:
        sock_con,(ip_scada,port_scada) = sock.accept()    
        logger.info("\nSe creo la coneccion con el scada en: ip=%s port=%d \n" %(ip_scada,port_scada))
    except Exception, e:
        logger.info("\nNo se pudo conecctar.\n")
        print e
        return 0
    
    datos = [SOF,   # Start of Frame 
             0,     # Quantity
             1,     # Origen
             2,     # Destino
             5,     # Secuencia
             0,     # Comando 0 (Peticion de estados y eventos)
             0,     # Status
             0,     # SeSync
             3,     # Cantidad de DI (Digital Input)        autom.logger.info('QTY OK, %d %s' % (entrada, type(entrada)))
             0x0C,  # PORTA
             0xfe,  # PORTB
             0xac,  # PORTC
             2,     # Cantidad de AI (Analog Input)
             0x03,  # AI0H  
             0xFF,  # AI0L
             0x02,  # AI1H
             0x00,  # AI1L
             0,     # Cantidad de evntos (por ahora sin eventos, poruqe son de 7 bytes
             ]
    datos[1] = len(datos) + 2 # Preagregamos el checksum
    datos += make_cs_bigendian(datos) # Concatenamos el checksum
    logger.info(' '.join( [('%.2x' % i).upper() for i in datos]))
    datos_cadena = ''.join([chr(i) for i in datos])
    assert len(datos) == len(datos_cadena), "Error en la conversion de cadena"
    while 1:
        trama = sock_con.recv(255);
        sock_con.send(datos_cadena)
        q = Paquete.from_octet_stream(trama)
        logger.info(q)
    return 0
        
   

if __name__ == '__main__':
    try:
        main()
    # Cuando recibe una interrupcion de teclado
    except KeyboardInterrupt:
        TERMINAR = True
        print "Saliendo del programa"
        