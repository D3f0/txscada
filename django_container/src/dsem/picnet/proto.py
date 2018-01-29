#! /usr/bin/env python
# -*- encoding: utf-8 -*-


# Manejo del path, puede traer problemas couando se freezee con py2exe
import sys
import os
# Para incluir 
sys.path.append(os.path.sep.join(('..','..')))

# Imports
from collections import OrderedDict
from checksum import make_cs, make_cs_pkg
from dtime import DTime
# Manejo de bits
from bitfield import bitfield
# Comprobar una cadena
from checksum import make_cs_bigendian, check_cs_bigendian


TCP_PORT = 9761

# Conforme a MICROCNET v.6
COMANDOS = {
    'REQ_DE_ESTADOS_Y_EVENTOS':         0x00,
    'REQ_MÁS_EVENTOS':                  0x01,
    'PUESTA_EN_HORA':                   0x02,
    'CONTROL':                          0x03,
    'FIJAR_PARAMETROS':                 0x04,
    'COMANDO_DE_REINICIO':              0x05,
    'REQ_DE_REGISTROS_DE_ESTADO':       0x06,
    'PROVOCA_NEV_EVENTOS_TIPO_02':      0x07,
    'ESCRIBIR_PARÁM_EEPROM':            0x08,
    'LEER_PARÁM_EEPROM':                0x09,
    'LIBRE':                            0x0a,
    'CONFIGIO_CAMBIAR_FUNC_DE_PORTS':   0x0b,
    
    'CAMBIO_DE_PROGRAMA':               0x10,
}

# Start of frame
SOF = 0xFE
# La menor longitud de paquete:
# Comando, Checksum Alto, Checksum Bajo
MIN_QTY = 8
# La maxima longitud de paquete...
MAX_QTY = 253

# Longitud máxima del payload
MAX_PAYLEN = MAX_QTY - MIN_QTY
#===============================================================================
# Los numeros de secuencia van de 0 a 255
#===============================================================================
MIN_SEQ = 0
MAX_SEQ = 250

MIN_ID = 1
MAX_ID = 63




#------------------------------------------------------------------------------ 
# Orden de bytes:
# Sof    Qty    Dst    Src    Sec    Com    Dato    BCCH    BCCL
#------------------------------------------------------------------------------
ORDEN_PAQUETE_MIN = (
     'SOF', 
     'QTY',
     'DST',
     'SRC',
     'SEC',
     'COM',
     #'DATO',
     'BCH',
     'BCL',
)

def arg_gen(prefix='A', length=3):
    ''' Generador para los nombres '''
    stop = length-1
    out_fmt = prefix + '%.' + str(stop) + 'x'
    tope = int('F'* stop, 16) + 1
    for i in xrange(tope):
        yield (out_fmt % i).upper()

 

class Paquete(OrderedDict):
    #TODO: Implementar la validación para el paquete
    def __init__(self, datos = None, auto_calc_cs = False):
        '''
        Constructor de el paquete.
        @precondition: Paquete válido
        @param trama_bytes: Cadena que viene por socket
        @param lista_enteros:
        @param validar: Dene ser validado
        '''
        self._auto_calc_cs = False
        lista_enteros = None
        if type(datos) == str:
            lista_enteros = [ord(i) for i in trama_bytes] 
        elif type(datos) == list:
            lista_enteros = datos
        
        # Si no se crea un paquete vacio
        if lista_enteros:
            self.fill(lista_enteros)
            
    def fill(self, lista_enteros):
        
        # Si no tiene dato
        tiene_datos = len(lista_enteros) > len(ORDEN_PAQUETE_MIN)
        
        if not tiene_datos:
            for i, d in enumerate(lista_enteros):
                self[ ORDEN_PAQUETE_MIN[i] ] = d
        else:
            for i, d in enumerate(lista_enteros):
                k = ORDEN_PAQUETE_MIN[i]
                self[ k ] = d
                if k == 'COM':
                    break
            long_datos = self['QTY'] - len(ORDEN_PAQUETE_MIN)
            
            i += 1
            
            for p, q in zip(range(long_datos), range(i , i+ long_datos ) ):
                k = ('D%.2x' % p).upper()
                self[ k ] = lista_enteros[ q ]
            # Copiamos finalmente el checksum
            self['BCH'], self['BCL'] = lista_enteros[-2:]
    
    
    def __getattribute__(self, name):
        # Si nos piden 
        key = name.upper()
        if super(Paquete, self).has_key(key):
            return super(Paquete, self).__getitem__(key)
        
        return super(Paquete, self).__getattribute__(name)
    
    def str_as_dict(self):
        return super(SortedDict, self).__str__()
    
    def octet_str(self):
        ''' Para mandarla a la red '''
        return ''.join([chr(b) for b in self.itervalues()])
    
    def hex_dump_key(self):
        return ', '.join(['%s: %s' % (k, ('%.2x' % v).upper()) for k, v in self.iteritems()])
    
    def hex_dump(self):
        return ' '.join([('%.2x' % v).upper() for v in self.itervalues()])
    
    def cs_ok(self):
        # Trama de enteros
        trama = [ v for v in self.itervalues() ]
        trama_sum = sum(trama[:-2])
        bch, bcl = make_cs(trama_sum)
        return self.get('BCH') == bch and self.get('BCL') == bch, bcl
        
    #TODO: Unificar este método con procesar
    @classmethod
    def from_octet_stream(cls, octet_stream):
        '''
        @deprecated: Este metodo no va más
        '''
        p = cls()
        if len(octet_stream) < 8:
            return None
        # Podemos hacer esto más corto, pero así es más gráfico
        p['SOF'] = ord(octet_stream[0])
        p['QTY'] = ord(octet_stream[1])
        p['DST'] = ord(octet_stream[2])
        p['SRC'] = ord(octet_stream[3])
        p['SEQ'] = ord(octet_stream[4])
        p['COM'] = ord(octet_stream[5])
        for i in range(len(octet_stream[5:-2])):
            p['D%.2x' % i] = ord(octet_stream[i])
        p['BCH'] = ord(octet_stream[-2])
        p['BCL'] = ord(octet_stream[-1])
        return p
    
    @classmethod
    def from_int_list(cls, int_list):
        return cls(lista_enteros = int_list)
    
    @classmethod
    def crear_estados_y_eventos(cls, origen, destino, secuencia):
        p = cls()
        p['SOF'] = SOF
        p['QTY'] = 8 # Este ya lo sabemos
        p['DST'] = destino
        p['SRC'] = origen
        p['SEQ'] = secuencia
        p['COM'] = COMANDOS['REQ_DE_ESTADOS_Y_EVENTOS']
        p['BCH'], p['BCL'] = cls.generar_checksum(p)
        return p
    
    @classmethod
    def crear_mas_eventos(cls, origen, destino, secuencia):
        p = cls()
        p['SOF'] = SOF
        p['QTY'] = 8 # Este ya lo sabemos
        p['DST'] = destino
        p['SRC'] = origen
        p['SEQ'] = secuencia
        p['COM'] = COMANDOS['REQ_MÁS_EVENTOS']
        p['BCH'], p['BCL'] = cls.generar_checksum(p)
        return p
    
    @classmethod
    def crear_control(cls, origen, destino, secuencia, puerto = None,
                      bit = None, estado = None, es_comando_indirecto = False):
        '''
        Si comando es 1, entocnes es una indirección. El tercer byte no 
        se tiene en cuenta.
        '''
        p = cls()
        p['SOF'] = SOF
        p['QTY'] = 10 # Este ya lo sabemos
        p['DST'] = destino
        p['SRC'] = origen
        p['SEQ'] = secuencia
        p['COM'] = COMANDOS['CONTROL']
        
        byte_0, byte_1 = bitfield(0), bitfield(0)
        # Es comando
        byte_0[7] = es_comando_indirecto and 1 or 0
        # 2 ^ 6 = 64 puertos
        byte_0[0:6] = puerto
        # Setear el bit a 1 o a 0
        byte_1[3] = estado
        
        if not es_comando_indirecto:
            # el nible superior no se utiliza
            byte_1[0:3] = bit
            
        
        p['A00'] = int(byte_0)
        p['A01'] = int(byte_1)
        p['BCH'], p['BCL'] = cls.generar_checksum(p)
        return p
    
    @classmethod
    def crear_escritura_registros_ram(cls, origen, destino, secuencia, x):
        p = cls()
        p['SOF'] = SOF
        p['QTY'] = 13 # Este ya lo sabemos
        p['DST'] = destino
        p['SRC'] = origen
        p['SEQ'] = secuencia
        p['COM'] = COMANDOS['FIJAR_PARAMETROS']
        # Esta secuencia de bytes es para seguridad, el micro controla que
        # existe esta secuencia de seugridad, ya que son comandos potencialmente
        # dañinos.
        p['A00'] = 0xAA
        p['A01'] = 0x55
        p['BCH'], p['BCL'] = cls.generar_checksum(p)
        return p
    
    
    @classmethod
    def crear_lectura_ram(cls, origen, destino, secuencia, page, addr, cant):
        p = cls()
        p['SOF'] = SOF
        p['QTY'] = 0 # Lo llenamos despues
        p['DST'] = destino
        p['SRC'] = origen
        p['SEQ'] = secuencia
        p['COM'] = COMANDOS['REQ_DE_REGISTROS_DE_ESTADO']
        p['A00'] = page
        p['A01'] = addr
        p['A02'] = cant
        p['BCH'], p['BCL'] = cls.generar_printchecksum(p)
        
        p['QTY'] = len(p)
        return p
        
    @classmethod
    def crear_lectura_eeprom(cls, origen, destino, secuencia, page, addr, cant):
        p = cls()
        p['SOF'] = SOF
        p['QTY'] = 0 # Lo llenamos despues
        p['DST'] = destino
        p['SRC'] = origen
        p['SEQ'] = secuencia
        p['COM'] = COMANDOS['LEER_PARÁM_EEPROM']
        p['A00'] = page
        p['A01'] = addr
        p['A02'] = cant
        p['BCH'], p['BCL'] = cls.generar_checksum(p)
        
        p['QTY'] = len(p)
        return p
    
    @classmethod
    def crear_puesta_en_hora(cls, origen, destino, secuencia):
        p = cls()
        p['SOF'] = SOF
        p['QTY'] = 0 # Lo llenamos despues
        p['DST'] = destino
        p['SRC'] = origen
        p['SEQ'] = secuencia
        p['COM'] = COMANDOS['PUESTA_EN_HORA']
        octetos = DTime.now().to_int_l()
        
        for nombre, octeto in zip(arg_gen('A'), octetos):
            p[nombre] = octeto
        p['BCH'], p['BCL'] = cls.generar_checksum(p)
        
        p['QTY'] = len(p)
        return p
    
    @classmethod
    def crear_paquete_custom(cls, origen, destino, secuencia, lista):
        assert type(lista) == list, "Debe ser una lista de enteros"
        assert all(map(lambda x: type(x) is int, lista)), \
                                            "Todos deben ser enteros"
        p = cls()
        p['SOF'] = SOF
        p['QTY'] = 0 # Lo llenamos despues
        p['DST'] = destino
        p['SRC'] = origen
        p['SEQ'] = secuencia
        p['COM'] = COMANDOS['PUESTA_EN_HORA']
        
        for nombre, octeto in zip(arg_gen('A'), lista):
            p[nombre] = octeto

        p['BCH'], p['BCL'] = cls.generar_checksum(p)
        p['QTY'] = len(p)
        return p
    
    @classmethod
    def crear_paquete_comando_custom(cls, origen, destino, comando, lista):
        assert type(lista) == list, "Debe ser una lista de enteros"
        assert all(map(lambda x: type(x) is int, lista)), \
                                            "Todos deben ser enteros"
        p = cls()
        p['SOF'] = SOF
        p['QTY'] = 0 # Lo llenamos despues
        p['DST'] = destino
        p['SRC'] = origen
        # El numero de secuencia es insertado por el scada
        p['SEQ'] = 0
        p['COM'] = comando
        
        for nombre, octeto in zip(arg_gen('A'), lista):
            p[nombre] = octeto

        p['BCH'], p['BCL'] = cls.generar_checksum(p)
        p['QTY'] = len(p)
        return p
    
    
    #===========================================================================
    #    
    #===========================================================================
    @staticmethod
    def generar_checksum(pkg):
        return make_cs_bigendian(pkg.values())
    
    @staticmethod
    def comprobar_checksum(pkg_con_cs):
        return check_cs_bigendian(pkg_con_cs.values())
    
    def __eq__(self, other):
        '''
        Operador de compraración de igualdad ==
        '''
        if type(self) != type(other):
            return False
#            raise TypeError("No se puede comparar %s con %s" % (type(self),
#                                                                 type(other)))
        for k, v in self.iteritems():
            if v != other[k]:
                return False
        return True
    

    def response(self, payload = None):
        ''' Genera el encabezado de respuesta en funcion a esta instancia.
        Se asume que solo se va a responder una vez a un paquete.
        Luego de este método, se debe llamar a set_payload si no se especifica
        un payload.'''
        p = Paquete()
        for n, k in zip(xrange(6), self):
            p[k] = self[k]
        # Inversión
        p['DST'] = self.SRC
        p['SRC'] = self.DST
        p['QTY'] = 0   # Por las dudas marcamos que no es un paquete completo
        if payload:
            p.set_payload(payload)
        return p
    
    def set_payload(self, payload):
        ''' Setea el pyaload y deja un paquete listo para ser enviado '''
        for k, v in zip(arg_gen(), payload):
            self[k] = v
        self['QTY'] = len(self) + 2
        self['BCH'], self['BCL'] = self.generar_checksum(self)
    
    def get_payload(self):
        ''' Retorna el payload del paquete '''
        return self.values()[6:-2]
    
    

if __name__ == '__main__':
    ''' Test del modulo de protocolo '''
    print "Creando paquete con origen 1, destino 3, y secuencia 2"
    p = Paquete.crear_estados_y_eventos(0x01, 0x03, 0x4)
    print "Datos = %s" % p 
    print "Volcado hexa:", p.hex_dump()
    print p.cs_ok()
    bytes = [ 0xFE, 0x08, 0x03, 0x01, 0x01, 0x03, 0x0A, 0xAA, 0xea, 0x03]
    q = Paquete(bytes)
    j = Paquete(bytes)
    print "Comparacion de igualdad entre Paquetes creados desde los mismos bytes:",
    print q == j
    j['SOF'] = 33
    print "Ahora la comprobacion deberia dar falso: ",
    print q == j
    print "Paquete q", q
    print "Paquete j", j
    print "Comprobacion de CS sobre q: ",q.cs_ok()
    p =  Paquete.crear_estados_y_eventos(1, 2, 3)
    print p
    print p.hex_dump()
    