#! /usr/bin/python
# -*- encoding: utf-8 -*-

'''
Mara checksum routines
'''
# TODO: Work wiht Streams instead of lists and Construct ULInt's

def make_cs(valor):
    '''
    Genra el checksum para la sumatoria
    '''
    valor &= 0xffff # Modulo 64k
    cs_h, cs_l = valor >> 8, valor & 0xff   # Parte alta, parte baja
    cs_h = 0xff - cs_h  # Complemento a 1 del octeto
    cs_l = 0xff - cs_l  # idem.
    return [cs_h, cs_l] # Retornar

make_cs_list = lambda l: make_cs(sum(l))
    
def make_cs_pkg(pkg):
    valor = sum([ord(b) for b in pkg.octet_str()])
    return make_cs(valor)
        
    
def check_cs(trama):
    payload, cs_h, cs_l = trama[:-4], trama[-4:-2], trama[-2:]
    check_h, check_l = make_cs(payload)
    return check_h == cs_h and check_l == cs_l


def sumar_cadena_hexa(cadena):
    assert type(cadena) is str, "%s no es una cadena" % cadena
    cadena = cadena.replace(' ','') # sin espacios
    total = 0
    while cadena:
        total += int(cadena[:2], 16) # Sumar en base 16 rebanadas de 2 caractlistaeres 
        cadena = cadena[2:]   # Descartamos lo que ya sumamos
    return total

def crear_checksum_hexa_cadena(trama):
    ''' Retorna el checksum como cadena'''   
    val = sumar_cadena_hexa(trama)
    h, l = make_cs(val)
    return "%2x %2x" % (h, l)

def verificar_checksum_hexa_cadena(cadena):
    ''' Comprueba el checksum de una trama completa '''
    cadena = cadena.replace(' ', '')
    assert len(cadena) > 5, "Cadena %s muy corta para verificar" % cadena
    trama, cs_h, cs_l = cadena[:-4], cadena[-4:-2], cadena[-2:]
    res_h, res_l = make_cs(sumar_cadena_hexa(trama))
    cs_h, cs_l = int(cs_h, 16), int(cs_l, 16)
    print cs_h, res_h, cs_l, res_l
    return res_h == cs_h and res_l == cs_l


def sum_big_endian(lista):
    '''
    Suma BIG ENDIAN
    '''
    # Para hacer Little Endian inicializar alto en false 
    suma, alto = 0, True
    for i in lista:
        if isinstance(i, basestring):
            i = ord(i)
        if alto:
            suma += i << 8
        else:
            suma += i
        alto = not alto
    return suma   

make_cs_bigendian = lambda l: make_cs(sum_big_endian(l))
format_cs = lambda l: ' '.join(map(lambda i: ('%x' % i).upper(), make_cs_bigendian(l)))
# Para que esta comprobación de bien, make_cs debe devolver una lista y
# no una tupla.
check_cs_bigendian = lambda l: make_cs_bigendian(l[:-2]) == l[-2:]

import sys
def main(argv = sys.argv):
    trama = [1, 2, 4, 5, 5, 6]
    
#    trama += make_cs_list(trama)
    trama = 'FE	08	01	40	80	10'
    print trama
    trama = map(lambda s: int(s, 16), trama.split())
    print format_cs(trama)
    
    trama = 'fe 08 02 01 21 10'
    trama = map(lambda s: int(s, 16), trama.split())
    print format_cs(trama)
    
    
    
if __name__ == "__main__":
    sys.exit(main())

