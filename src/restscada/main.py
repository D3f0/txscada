#!/usr/bin/env python
# encoding: utf-8
'''
'''
import sys
from config import Config
try:
    import restscada
except ImportError:
    sys.path.append('..')

from restscada.rest.site import site
from twisted.internet import reactor, error


def main(argv = sys.argv):
    '''
    Arrancar el server
    '''
    print "Arrancando el server"
    try:
        
        reactor.stop()
    except error.ReactorNotRunning:
        pass
    reactor.listenTCP(9000, site )
    reactor.run()
    
    
if __name__ == "__main__":
    # TODO: Paramtros de linea de comandos
    # TODO: Cargar configuracion basada en objeto config.Config
    main()
    
