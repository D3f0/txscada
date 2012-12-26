#! /usr/bin/env python
# -*- encoding: utf-8 -*-


class bitfield(object):
    '''
    Clase dedicada al slicing de bytes
    '''
    def __init__(self, value=0):
        if type(value) == list:
            self._d = bitfield.bytes_a_entero(value)
        elif type(value) == str:
            self._d = bitfield.bytes_a_entero([ ord(c) for c in value ])
        else:
            self._d = value

    def __getitem__(self, index):
        return (self._d >> index) & 1

    def __setitem__(self, index, value):
        value = (value & 1L) << index
        mask = (1L) << index
        self._d = (self._d & ~mask) | value

    def __getslice__(self, start, end):
        mask = 2L ** (end - start) - 1
        return (self._d >> start) & mask

    def __setslice__(self, start, end, value):
        mask = 2L ** (end - start) - 1
        value = (value & mask) << start
        mask = mask << start
        self._d = (self._d & ~mask) | value
        return (self._d >> start) & mask

    def __int__(self):
        return self._d

    def __str__(self):
        return "%d" % int(self)

    def to_bin(self, length=8):
        ''' Retorna al representación en formato cadena de 1 y 0s.'''
        return int2bin(int(self), length)

    @staticmethod
    def bytes_a_entero(enteros):
        ''' Convertir una lista de enteros para operaciones de bits'''
        assert type(enteros) == list, "Los bytes no es una lista de enteros"

        result = 0
        enteros.reverse()
        for potencia, valor in enumerate(enteros):
            result += valor << (8 * potencia)
        return result

def int2bin(i, length=8):
    ''' Retorna la representacion binaria de un entero.

    '''
    retval = ''
    while i:
        retval += str(i % 2)
        i >>= 1
    # Damos vuelta la cadena y le plaicamos los ceros que falten
    return retval[::-1].rjust(length, '0')

def iterbits(ints, length=16):
    '''
    Iterate over bits of many integers
    '''
    for val in ints:
        bf = bitfield(val)
        for i in range(length):
            retval = bf[i]
            #print retval
            yield retval

def multibitfield_iter(bitfields, slices, input_length=16):
    pass

bin = lambda i: bitfield.bin(i)

def test():
    print "Prueba de la estructura de control de bits"
    k = bitfield()
    k[2:7] = 7
    print k
    print k.to_bin()
    print "Nibble menos significativo", int2bin(k[0:4])

    print "Paso a paso"
    print "-"*40
    print "a = 0"
    a = bitfield(0)
    print a
    print "a[3] = 1"
    a[3] = 1
    print a
    print "a[0:3]"
    print a[0:3]
    print "a[0:3] = 7"
    a[0:3] = 7
    print a.to_bin()

    print a
    print a.to_bin()
    print "-"*40


if __name__ == "__main__":
    test()
