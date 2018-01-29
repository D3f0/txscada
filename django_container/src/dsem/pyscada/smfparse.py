#! /usr/bin/env python
# -*- encoding: utf-8 -*-


from itertools import izip
from twisted.python import log
NOMBRES_DATOS_ORDENADOS = '''
    id_CO,id_UC,Zona,CanMovi,timovH,timovL 
    '''
    # No va
    #,CicloSm1,RetGen1,
    #CicloSem2,RetGen2,EntAgenda,PeriodoToma,PerEvLamp
    
    

NOMBRES = map( str.strip, NOMBRES_DATOS_ORDENADOS.strip().split(','))

# DEBUG
#print NOMBRES

def iter_two(tope, ini = 0, step = 2):
    return izip(xrange(ini, tope, step), xrange(ini + step, tope + step, step))

def parse_smf(fname):
    '''
    Devuelve un diccionario en funcion de los archivos de configuracion
    generados por el configurador. Tomamos solamente la primera linea
    de la configuración.
    Si se produce un error, se devuelve un diccionario vacío.
    '''
    fp = open(fname)
    datos = {}
    linea_0 = fp.readline().strip()
    cadena = linea_0.split(";")[0].strip()
    try:
        for nombre, posiciones in zip( NOMBRES, iter_two(len(NOMBRES)*2)):
            #print nombre, posiciones
            dos_caracteres = cadena[ posiciones[0] : posiciones[1] ]
            log.msg('Leyendo: %s en %d:%d' % (nombre, posiciones[0], posiciones[1] ))
            datos[ nombre ] = int(dos_caracteres, 16)
        
    except (ValueError, TypeError, IOError):
        pass
    fp.close()
    return datos
    
    
import sys

def main(argv = sys.argv[1:]):
    ''' Funcion main '''
    if not len(argv):
        print "Se debe pasar un archivo SMF como arguento"
        return
    print parse_smf(argv[0])
    
if __name__ == "__main__":
    sys.exit(main())

    
        