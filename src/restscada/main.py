'''
Created on 06/08/2009

@author: defo
'''
import sys
try:
    import restscada
except ImportError:
    sys.path.append('..')

from restscada.rest.site import site
from twisted.internet import reactor

if __name__ == "__main__":
    # TODO: Paramtros de linea de comandos
    # TODO: Cargar configuracion basada en objeto config.Config
    
    reactor.listenTCP(9000, site )
    reactor.run()