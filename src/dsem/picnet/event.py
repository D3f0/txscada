#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
from bitfield import bitfield, int2bin
from datetime import datetime, timedelta
from itertools import izip

def range_2_pot(stop, start = 0, step = 8):
    return izip(xrange(start, stop, step), xrange(start + step, stop + 1, step))
    
bin = lambda s: int(s, 2)


class EventoConUC(object):
    '''
    Encapsula el evento.
    '''
    DATE_FMT = '%A %d-%m-%y %H:%M:%S'
    
    def __init__(self, cadena):
        if type(cadena) == str:
            cadena = [ ord(c) for c in cadena ]
        assert len(cadena) == 8, "Longitud de evento incrrecta"
        
        self.cadena = cadena
        self._parse_bytes()
        
        
    def _parse_bytes(self):
        '''
        Parsea la entrada basandose en self.cadena.
        Este método debe ser sobrecargado en las subclases en el caso
        de cambiar la decodificación de evento.
        '''
        # Primera parte
        bf = bitfield(self.cadena[0])
        self.tipo, self.uc = bf[6:8], bf[0:6]
        # Segunda parte
        bf = bitfield(self.cadena[1])
        self.port, self.bit, self.event = bf[4:8], bf[1:4], bf[0:1]
        bf = bitfield(self.cadena[2:6])
        
        # Cuatro bytes de fecha
        
        self.y, self.d, self.h, self.s = bf[26:32], bf[17:26], bf[12:17], bf[0:12]
        
        self.cseg, self.dseg = self.cadena[6:8]
        self.microsceconds = self.dseg * 10000 +  self.cseg * 100
    
    
    def _date_bytes(self):
        return self.cadena[2:]
            
    def datetime(self):
        dt = datetime(year = 2000 +  self.y, day=1, month=1, 
                      microsecond = self.microsceconds % 999999 )
        # El 1 es el 1 de enero
        dt += timedelta(days = self.d - 1 , hours = self.h, seconds = self.s)
        return dt
    
    def __str__(self):
        salida =  'Tipo: %d Unidad de control: %d\n' % (self.tipo, self.uc)
        salida += 'Puerto: %d Bit: %d Evento %d\n' % (self.port, self.bit, 
                                                      self.event)
        salida += '%s.%s\n' % (self.datetime().strftime(EventoConUC.DATE_FMT), 
                               self.datetime().microsecond)
        return salida
    
    @classmethod
    def create(cls, tipo = 1, uc = 2, port = 0, bit = 0, status = 0, date_time = None, cseg = 0, dmseg = 0, int_output = False):
        '''
        Crear un evento a partir de los parametros.
        @return: Lista de enteros, correspondiendtes a los bytes a enviar
        '''
        if not date_time:
            date_time = datetime.now()

        pkg = []
        cls._pack_tuc(pkg, **locals())
        cls._pack_pbe(pkg, **locals())
        cls._pack_date(pkg, **locals())
        
        if int_output:
            # Salida como enteros
            return pkg
        # Salida como cadena
        return ''.join(map(chr,pkg))
    
    @staticmethod
    def _pack_tuc(part_list, **args):
        '''
        @arg part_list: Argumento de entrada salida
        '''
        byte = bitfield(0)
        byte[6:8] = args['tipo']
        byte[0:6] = args['uc']
        part_list.append(int(byte))
    
    @staticmethod
    def _pack_pbe(part_list, **args):
        '''
        @arg part_list: Argumento de entrada salida
        '''
        byte = bitfield(0)
        byte[0] = args['status']
        byte[1:4] = args['bit']
        byte[4:8] = args['port']
        part_list.append(int(byte))
    
    @staticmethod
    def _pack_date(part_list, **args):
        '''
        @arg part_list: Argumento de entrada salida
        '''
        # Creamos un bitfield para la fecha, este va a ser de 32 bits
        bytes = bitfield(0)
        date_time = args['date_time']
        bytes[26:32] = date_time.year - 2000 # Año desde el 2000
        bytes[17:26] = date_time.date().timetuple()[7] # Dia del año
        bytes[12:17] = date_time.hour
        bytes[00:12] = date_time.minute * 60 + date_time.second
        
        # Separamos los bytes
        init_tope = list(range_2_pot(32))
        init_tope.reverse()
        for init, tope in init_tope:
            part_list.append(int(bytes[init:tope]))
        
        # Dmseg y cDmseg
        part_list.append(args['cseg'] % 100)
        part_list.append(args['dmseg'] % 100)
    
    
    
    @classmethod
    def create_ints(cls, *largs, **kwargs):
        kwargs.update(int_output = True)
        return cls.create(*largs, **kwargs)
        

def humstr2ints(bin_str):
    '''
    Recibe una cadena de binaria (con posibles espacios y comentarios #) y
    separa de a 8 bits, retornando la lista de enteros.
    '''
    enteros = []
    # Por cada linea
    for c in bin_str.split('\n'):
        # Quitamos comentarios y nos quedamos con la parte de la izquierda
        c = c.split('#')[0].strip()
        # Sacamos espacios
        c = c.replace(' ', '') 
        if not c:
            continue
        # Por cada bit
        for i in range(0, len(c), 8):
            enteros.append( int(c[i:i + 8], 2))
    return enteros

class EventoCodigo(EventoConUC):
    '''
    Encapsula la nueva version de evento que utiliza los bis de UC para Código
    (Prioridad).
    '''
    
    def _parse_bytes(self):
        '''
        Parsea la entrada basandose en self.cadena.
        Este método debe ser sobrecargado en las subclases en el caso
        de cambiar la decodificación de evento.
        '''
        # Primera parte
        bf = bitfield(self.cadena[0])
        self.tipo, self.prio, self.codigo  = bf[6:8], bf[4:6], bf[0:4]
        # Segunda parte
        bf = bitfield(self.cadena[1])
        self.port, self.bit, self.event = bf[4:8], bf[1:4], bf[0:1]
        bf = bitfield(self.cadena[2:6])
        
        # Cuatro bytes de fecha
        
        self.y, self.d, self.h, self.s = bf[26:32], bf[17:26], bf[12:17], bf[0:12]
        
        self.cseg, self.dseg = self.cadena[6:8]
        
        self.microsceconds = self.dseg * 100 +  self.cseg * 10000
        # print self.microsceconds
    
    @classmethod
    def create(cls, tipo = 1, codigo = 1, prio = 3, port = 0, bit = 0, status = 0, date_time = None, cseg = 0, dmseg = 0, int_output = False):
        '''
        Crear un evento a partir de los parametros.
        @return: Lista de enteros, correspondiendtes a los bytes a enviar
        '''
        if not date_time:
            date_time = datetime.now()

        pkg = []
        cls._pack_tuc(pkg, **locals())
        cls._pack_pbe(pkg, **locals())
        cls._pack_date(pkg, **locals())
        
        if int_output:
            # Salida como enteros
            return pkg
        # Salida como cadena
        return ''.join(map(chr,pkg))
    
    
    @staticmethod
    def _pack_tuc(part_list, **args):
        '''
        @arg part_list: Argumento de entrada salida
        '''
        byte = bitfield(0)
        byte[6:8] = args['tipo']
        byte[4:6] = args['prio']
        byte[0:4] = args['codigo']
        part_list.append(int(byte))

    def __str__(self):
        salida =  'Tipo: %d Codigo: %d Prioridad: %d\n' % (self.tipo, self.codigo, self.prio)
        salida += 'Puerto: %d Bit: %d Evento %d\n' % (self.port, self.bit, 
                                                      self.event)
        salida += '%s.%s\n' % (self.datetime().strftime(EventoConUC.DATE_FMT), 
                               self.datetime().microsecond)
        return salida



#===============================================================================
# test_evento_v11
#===============================================================================
def test_evento_v11():

    cadena_evento = '''
        10 100101                     # Tipo y uC(3)
        1001 101 1                    # Port Bit Event
        001000 001000100 00001 000100001001  # Año(6) Día(9) Hora(5) Segs(12)
        00000011                      # Centisegundo
        00000011                      # Decima de milisegundo
    '''
    
    enteros = humstr2ints(cadena_evento)
    
    print enteros
    print "-" * 10
    print "Evento"
    print "-" * 10
    e1 = EventoConUC(enteros)
    print e1
    print "=" * 40
    ev = EventoConUC.create(tipo=2, uc=37, port=9, bit=5, status=1, date_time=datetime.now())
    
    print "Cadena:" , map(ord, ev)
    e2 = EventoConUC(ev)
    print e2
    print "Evento1:", map(int2bin, e1._date_bytes())
    print "Evento2:", map(int2bin, e2._date_bytes())
    
    ints = EventoConUC.create_ints(tipo=2, uc=37, port=9, bit=5, status=1, date_time=datetime.now())
    print ints
    print "Evento2:", map(int2bin, EventoConUC.create_ints(tipo=2, uc=37, port=9, bit=5, status=1, date_time=datetime.now()))

#===============================================================================
# test_evento_v12
#===============================================================================
def test_evento_v12():

    cadena_evento = '''
        10 10 0101                   # Tipo(2), Prioridad(2), Código (4)
        1001 101 1                    # Port Bit Event
        001000 001000100 00001 000100001001  # Año(6) Día(9) Hora(5) Segs(12)
        00000011                      # Centisegundo
        00000011                      # Decima de milisegundo
    '''
    
    enteros = humstr2ints(cadena_evento)
    
    print enteros
    print "-" * 10
    print "Evento"
    print "-" * 10
    e1 = EventoCodigo(enteros)
    print e1
    print "=" * 40
    ev = EventoCodigo.create(tipo=2, codigo=3, port=9, bit=5, status=1, date_time=datetime.now())
    
    print "Cadena:" , map(ord, ev)
    e2 = EventoCodigo(ev)
    print e2
    print "Evento1:", map(int2bin, e1._date_bytes())
    print "Evento2:", map(int2bin, e2._date_bytes())
    
    ints = EventoCodigo.create_ints(tipo=2, codigo=3, port=9, bit=5, status=1, date_time=datetime.now())
    print ints
    print "Evento2:", map(int2bin, EventoCodigo.create_ints(tipo=2, codigo=3, port=9, bit=5, status=1, date_time=datetime.now()))



def main():
    test_evento_v11()
    print "^" * 50
    test_evento_v12()

if __name__ == "__main__":
    sys.exit(main())


