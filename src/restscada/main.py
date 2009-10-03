#!/usr/bin/env python
# encoding: utf-8
'''
Servidor Web que publica los recursos REST.
'''
import sys

try:
    import restscada
except ImportError:
    sys.path.append('..')

try:
    from config import Config
except ImportError:
    print "No se encuentra el módulo de configuración 'config'"
    print "Por favor instalelo desde 'http://pypi.python.org/pypi/config/0.3.7'"
    print "o mediante la orden easy_install config"
    print "si posee pip (reemplazo sugerido de easy_install), realize pip install config"
    sys.exit(-2)


from restscada.rest.site import site
from twisted.internet import reactor, error


def main(argv = sys.argv):
    '''
    Arrancar el server
    '''
    print "Arrancando el server"
    try:
        config = Config(open('config.cfg'))
    except Exception, e:
        print "No se puede leer la configuracion"
        print "Obtenga una del repositorio"
        sys.exit(3)

    reactor.listenTCP(config.webserver.port, site )
    reactor.run()
    
    
if __name__ == "__main__":
    # TODO: Paramtros de linea de comandos
    # TODO: Cargar configuracion basada en objeto config.Config
    main()
    
