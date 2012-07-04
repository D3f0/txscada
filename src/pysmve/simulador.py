# encoding: utf-8

import sys
import argparse
from twisted.internet import protocol, reactor
from twisted.python import log

from collections import namedtuple

class Simulador(protocol.Protocol):
    def __init__(self, *largs, **kwargs):
        print "Simulador", largs, kwargs
        
    def connectionMade(self):
        """docstring for connectionMade"""
        log.msg("Conexion %s" % self.transport)
    
class SimuladorFactory(protocol.Factory):
    protocol = Simulador
    
def setup():
    # Copiado del XLS
    nombres = 'Offset	Dir485Ied	CanVarSys	CanDIS	CanAIs'
    tabla = '''
    0	1	6	2	1
    1	2	2	4	2
    2	3	2	4	2
    3	4	2	4	2
    4	5	2	4	2
    5	0	0	0	0
    6	0	0	0	0
    7	0	0	0	0
    8	0	0	0	0
    9	0	0	0	0
    10	0	0	0	0
    11	0	0	0	0
    12	0	0	0	0
    13	0	0	0	0
    14	0	0	0	0
    15	0	0	0	0
    '''
    filas = [ line for line in tabla.split('\n') ]
    tabla = [ fila.strip().split() for fila in filas ]
    tipo = namedtuple('fila', nombres.split())
    for fila in tabla:
        if not len(fila): continue
        yield tipo._make(fila)
        

def main(argv=sys.argv):
    """Función"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=3456)
    options = parser.parse_args()
    log.startLogging(sys.stdout)
    for confied in setup():
        print confied
        
    reactor.listenTCP(options.port, SimuladorFactory())
    reactor.run()
    
if __name__ == '__main__':
    main()