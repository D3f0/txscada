#coding: utf8
'''
Created on 03/10/2009

@author: defo
'''

from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log
from config import Config
from simplejson import dumps
from jinja2.loaders import FileSystemLoader
from twisted.python.util import println
from twisted.web.static import File
import sys
import os
from pprint import pformat
from twisted.internet import defer
from twisted.internet import threads
from jinja2 import Environment, PackageLoader
import time
from twisted import copyright

class Root(resource.Resource):
    '''
    Recurso base que se renderiza en /
    '''

    def getChild(self, path, request):
        if not path or path == '/':
            return self
        return resource.Resource.getChild(self, path, request)
    
    def render_GET(self, request):
        return render_to_template(request, 'site.html', {})

sys.path.append('../..')
import restscada
path = os.path.join(os.path.abspath(restscada.__path__[0]), 'templates')
env = Environment( loader = FileSystemLoader(path) ) 


#===============================================================================
# Deferreds para le manejo de templates
#===============================================================================
def get_template(template_name):
    #log.msg("Getting template", template_name)
    template = env.get_template(template_name)
    #log.msg("Template", template)
    return template

def println_stop_reactor(e):
    println(e)
    reactor.stop()

def do_response(processed_template, request):
    request.setHeader("Content-type", 'text/html; charset=UTF-8')
    request.setHeader("Server", "RestScada Server based on Twisted %s" % copyright.version)
    request.write(processed_template)
    request.finish()
    request.transport.loseConnection()
    
def render_to_template(request, template_name, data):
    d = threads.deferToThread(get_template, template_name)
    d.addCallback(lambda t: t.render(data).encode('utf8'))
    d.addCallback(do_response, request)
    return server.NOT_DONE_YET
    

class NotificationTestResource(resource.Resource):
#    def __init__(self):
#        resource.Resource.__init__(self)
#        import restscada
#        
#        path = os.path.join(os.path.abspath(restscada.__path__[0]), 'templates')
#        log.msg('Tempaltes path = ', path, 'exists?', os.path.exists(path))
#        self.template_loader = Environment( loader = FileSystemLoader(path) )
#        log.msg(self.template_loader)
    def getChild(self, *largs):
        return self
        
    def render_GET(self, request):
        #request.setHeader("Content-type", 'text/html; charset=UTF-8')
        #template = self.template_loader.get_template('index.html')
        #title = u"Título de la cosa"
        
        #return template.render(locals()).encode('utf8')
        
        return render_to_template(request, 'index.html', {
                                                          'title': "Probando Twisted", 
                                                          'time': time.time(), 
                                                          'time_time': time.time,
                                                          }) 


class NotificationHub(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        # Cada cliente se crea
        self.clients = {}
        # Teimpo en mS hasta que un cliente se desconecta
        self.client_expiration_delay = 4000
    
    def render_GET(self, request):
        request.setHeader('Content-Type', 'text/plain')
        def answer_later(request):
            #from ipdb import set_trace; set_trace()
            request.write(dumps(
                                {'/co/1': {'ev':1, 'timestamp':3020232}
                                 
                                 }
                                
                                
                                ))
            request.finish()
            
        reactor.callLater(0, answer_later, request)
        
        return server.NOT_DONE_YET
    
    
    
def main(argv = sys.argv):
    log.startLogging(sys.stderr, setStdout = False)
    cfg = Config(open('config.cfg'))
    root = Root()

    push = NotificationHub()
    root.putChild('static', File('static'))
    push.putChild('test', NotificationTestResource() )
    root.putChild( 'push',  push )
    site = server.Site(root)
    
    reactor.listenTCP(cfg.webserver.port, site)
    reactor.run()

if __name__ == "__main__":
    
    main()



