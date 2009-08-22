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
    def __new__(cls, name, bases, *largs, **kwargs):
        #print cls, name, largs, kwargs
        return type(name, *largs, **kwargs)

class RestPublisherBase(object):
    __metaclass__ = RestPubisherMetaclass

    
class SARestPublisher( RestPublisherBase ):
    sa_class = None

def main(argv = sys.argv):
    from twisted.internet import reactor
    
    class MyRoot(RestRsourcePublisher):
        ''' Definimos un recurso de prueba'''
        pass
    
    m = MyRoot()
    sa_entity = "En progreso"
    m.register(sa_entity)
    root = MyRoot()
    site = server.Site(root)
    reactor.listenTCP(8003, site) #@UndefinedVariable
    reactor.run() #@UndefinedVariable
    
    return
    
if __name__ == "__main__":
    main()
    