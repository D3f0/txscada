#!/usr/bin/env python
#coding: utf-8
'''
Created on 28/09/2009

@author: defo

Utilizar las apis descritas en

http://twistedmatrix.com/projects/web/documentation/howto/using-twistedweb.html#auto2

'''
import sys
from twisted.web import server, resource, static
from twisted.web.error import NoResource
from twisted.internet import reactor
from config import Config
import re
from twisted.python import log
from django.utils.datastructures import SortedDict
from pprint import pformat

class ResourceEntryWrapper(object):
    def __init__(self, callback_or_class, supported_methods = None):
        if not supported_methods:
            supported_methods = ('GET', )
            
        self.callback = callback_or_class
    
    def __call__(self, request, *largs, **kwargs):
        log.msg('Calling %s with %s %s' %(self.callback, largs, kwargs))
        return self.callback(request, *largs, **kwargs)

class Simple(resource.Resource):
    #isLeaf = True
    
    def __init__(self, *largs, **kwargs):
        # Almacenamos los patrenos de las urls en 
        # un diccionario ordenado
        resource.Resource.__init__(self, *largs, **kwargs)
        self.patterns = SortedDict()
    
    def getChildWithDefault(self, path, request):
#    def getChild(self, name, request):
        # El comportamiento por defecto es el de los Resource
        
        res = resource.Resource.getChildWithDefault(self, path, request)
        if not isinstance(res, NoResource):
            return res
        # Si no encontramos el recurso
        for uri_regex, entry_point in self.patterns.iteritems():
            match = uri_regex.match(request.path)
            if match:
                
                log.msg("Match!!!")
                break
        log.msg(u"*"*40)
        return self
        
        

    def render_GET(self, request):
        return "Hello, world! Me encuentro en %r." % (request.prepath,)
 
    
    def uri_map(self, uri_regex, func, opts = None , **kwargs):
        '''
        Mapea una URL en una función
        '''
        if not opts:
            opts = {}
        if not opts.has_key('method'):
            opts['method'] = ('GET', )
            
        regex = re.compile(uri_regex)
        self.patterns[regex] = ResourceEntryWrapper(func)
        log.msg(pformat(self.patterns))

class RestSite(server.Site):
    '''
    Site que permite mapear urls mediante expresiones regulares además del sistema
    de recursos tradicional de Twisted.
    '''
    def __init__(self, *largs, **kwargs):
        server.Site.__init__(self, *largs, **kwargs)
        self.url_patterns = SortedDict()
        
    def getResourceFor(self, request):
        log.msg("El sitio busca el recurso %s" % request.path)
        res = server.Site.getResourceFor(self, request)
        if not isinstance(res, NoResource):
            return res
        
        for regex, callback in self.url_patterns.iteritems():
            norm_path = request.path[1:]
            log.msg("Buscando %s" % norm_path)
            match = regex.match(norm_path)
            if match:
                kwargs = match.groupdict()
                # Generamos un Resource
                class GeneratedResource():
                    def render(self, request):
                        return callback(request, **kwargs)
                    
                return GeneratedResource()
            
        log.msg(res)
        return res          
    
    def register_uri(self, uri_regex, callback, **opts):
        if uri_regex[0] == '/':
            uri_regex = uri_regex[1:]
        regex = re.compile(uri_regex)
        self.url_patterns[regex] = callback
         
    
def simple_view(request, co_id, format):
    
    return """<html><head>
                    <title>Concentrador %(co_id)s</title>
                    </haed>
                <body>
                    <h3>Concentrador %(co_id)s</h3>
                    
                </body>
    </html>
    """ % locals()

def mostrar_concentradores(request):
    request.setHeader('conent-type', 'text/plain')
    
    return "Un monton de concentradores %s" % pformat(locals())

def main(argv = sys.argv):
    log.startLogging(sys.stdout, setStdout = False)
    config = Config('config.cfg')
    site = RestSite(resource.Resource())
    
    site.register_uri(r'/co/(?P<co_id>\d{1,8})/?(?:.(?P<format>[json|html]))?$', simple_view)
    site.register_uri(r'/co/$', mostrar_concentradores)
    site.register_uri(r'/co/(?P<co_id>\d{1,8})/?$', simple_view)
    site.register_uri(r'/co/(?P<co_id>\d{1,8})/uc/(?P<uc_id>\d{1,8})/?$', simple_view)
    
    reactor.listenTCP(config.webserver.port, site) #@UndefinedVariable
    reactor.run() #@UndefinedVariable
    
if __name__ == "__main__":
    main()
    
    
    








