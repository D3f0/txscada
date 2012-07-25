#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from bitfield import bitfield
from datetime import datetime, timedelta

class DTime(object):
    '''
    Esta clase trabaja con la codificacion en bits de la fecha para Picnet.
    Version < 14.
    '''
    def __init__(self, input_ = None):
        '''
        @param input_: Cadena de 1 y 0's (opcional espacioes), cadena
        de caracteres tal cual vienen del socket, entero (32bits) o lista
        de enteros.
        '''
        if not input_:
            self.__bf = bitfield(0)
        elif type(input_) == str:
            # Es una cadena binara?
            if all(map(lambda c: c in '01 ', input_)):
                input_ = input_.replace(' ', '')
                i = int(input_, 2)
                self.__bf = bitfield(i)
            # cadena normal, tal cual sacada del socket
            else:
                self.__bf = bitfield([ ord(c) for c in input_])
        elif type(input_) == int or type(input_) is long:
            self.__bf = bitfield(input_)
            
        elif type(input_) == list and all(map(lambda i: type(i) is int, input_)):
            self.__bf = bitfield(input_)
            
        else:
            raise ValueError('No se puede crear DTime a partir de %s' % input_)
    
    def get_y(self):
        return self.__bf[26:32]
    
    def get_d(self):
        return self.__bf[17:26]
    
    def get_h(self):
        return self.__bf[12:17]
    
    def get_s(self):
        return self.__bf[ 0:12]
    
    def set_y(self, y):
        self.__bf[26:32] = y
        
    def set_d(self, d):
        self.__bf[17:26] = d
    
    def set_h(self, h):
        self.__bf[12:17] = h
    
    def set_s(self, s):
        self.__bf[ 0:12] = s
    
    y = property(get_y, set_y, doc = "Año")
    d = property(get_d, set_d, doc = "Día")
    h = property(get_h, set_h, doc = "Horas")
    s = property(get_s, set_s, doc = "Segundos")
    
    def __int__(self):
        return int(self.__bf)
    
    def __eq__(self, other):
        return self.y == other.y and self.d == other.d and self.h == other.h\
                     and self.s == other.s
    
    def __gt__(self, other):
        return self.to_datetime() > other.to_datetime()
    
    def __gte__(self, other):
        return self.to_datetime() >= other.to_datetime()
    
    def __lt__(self, other):
        return self.to_datetime() < other.to_datetime()
    
    def __lte__(self, other):
        return self.to_datetime() <= other.to_datetime()
    
    def to_datetime(self):
        dt = datetime(year = 2000 +  self.y, day=1, month=1)
        dt += timedelta(days = self.d, hours = self.h, seconds = self.s)
        return dt
    
    def to_str(self):
        ''' No confunidr con __str__, genera la representacion para envio por 
            socket
        '''
        int_l = []
        for i in range(0,32, 8):
            int_l.append( self.__bf[i: i+8])
        return (''.join([chr(c) for c in int_l]))[::-1]
    
    def __str__(self):
        return self.to_datetime().strftime('%d/%m/%y %H:%M:%S')
    
    @classmethod
    def from_datetime(cls, dt = None):
        if not dt:
            dt = datetime.now()
        retval = cls()
        retval.y = dt.year - 2000
        retval.d = (dt - datetime(dt.year, 1, 1)).days
        retval.h = dt.hour
        retval.s = dt.minute * 60 + dt.second 
        return retval
    
    def to_hex(self, sep = ' '):
        return (sep.join(['%.2x' % i for i in self.to_int_l()])).upper()
    
    def to_int_l(self):
        ''' Retorna la lista de enteros '''
        return [ ord(x) for x in self.to_str() ]
    
    @classmethod
    def now(cls):
        return cls.from_datetime(datetime.now())


if __name__ == '__main__':
    # d = DTime(2**32 +  2 ** 31)
    d = DTime.now()
    print d.to_datetime() 
    
    print "y=%d d=%d h=%d s=%d" % (d.y, d.d, d.h, d.s)
    print
    print "Prueba de integridad de str"
    a = DTime.now()
    print "Ahora:", a
    b = DTime(a.to_str())
    print "Reconstruccion a partir de to_str():", b
    print "A == B?", a == b 
    print a.to_hex()