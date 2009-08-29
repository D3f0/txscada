'''
Created on 06/08/2009

@author: defo
'''
from restscada.rest.site import site
if __name__ == "__main__":
    # TODO: Paramtros de linea de comandos
    # TODO: Cargar configuracion basada en objeto config.Config
    
    reactor.listenTCP(9000, site )
    reactor.run()