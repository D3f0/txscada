#!/usr/bin/env python
'''
Mockup
'''

from twisted.web import resource, server
import sys

class RestRsourcePublisher(resource.Resource):
    def register(self, rest_class):
        pass

class RestPubisherMetaclass(type):
    def __new__(cls, name, bases, namespace):
        #print cls, name, largs, kwargs
        inst = type(name, bases, namespace)
        # Generar las instancias de resource
        return inst

class RestPublisherBase(object):
    __metaclass__ = RestPubisherMetaclass


class SARestPublisher( RestPublisherBase ):
    # Los atributos de clase son parametros
    # de configuración
    sa_class = None
    name = 'co'
    name_plural = 'cos'
    
    # Debería generar los recursos
    # /co/
    # /cos/
    
    
    
def main(argv = sys.argv):
    from twisted.internet import reactor
    
    class MyRoot(RestRsourcePublisher):
        ''' Definimos un recurso de prueba'''
        pass
    puerto = 8003
    m = MyRoot()
    sa_entity = "En progreso"
    m.register(sa_entity)
    root = MyRoot()
    site = server.Site(root)
    reactor.listenTCP(puerto, site) #@UndefinedVariable
    print "Correindo en locahost:%d" % puerto
    reactor.run() #@UndefinedVariable
    
    return
    
if __name__ == "__main__":
    main()
    