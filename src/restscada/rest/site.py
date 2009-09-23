'''
Created on 29/08/2009

@author: defo, lau
'''

from twisted.web import server, resource, static
from twisted.web.error import NoResource
import rest_simulator

class UserAgentDelegate(object):
    def render(self):
        raise NotImplementedError("You must sublcass this method")

#class HTMLDelegate():
class ResponseWriter(object):
    '''
    Encargado de escribir la respuesta
    '''
    pass


class RESTfulResource( resource.Resource ):
    
    
    def render(self, request):
        
        response_delegate = self.responseDelegateFactory(request.method)
        
        try:
            return response_delegate.render()
        except Exception, e:
            return "Error"
    
#    def __getattr__(self, name):
#        index = name.index('render_')
#        if index:
#            method_name = name[index:]
#            xxxx.yyyy

class Redirector(resource.Resource):
    def __init__(self, to, **kwargs):
        self.to = to
        
    def render(self, response):
        response.setResponseCode(301)
        response.setHeader('Location', self.to)
        response.finish()

class BaseResource(resource.Resource):
    
    def __init__(self, *largs, **kwargs):
        resource.Resource.__init__(self, *largs, **kwargs)
        static_res = static.File('static')
        self.putChild('static', static_res )
        self.putChild('', Redirector('/static/'))
        self.putChild('scada', Scada() )
        
        
class TestResource(resource.Resource):    
    isLeaf = True
    
    def __init__(self, an_object):
        self.obj = an_object
        
    def render_GET(self, request):
        return  rest_simulator.make_html(self.obj)
        
    render = render_GET
        
class TestBaseResource(resource.Resource):    
    def add_child(self, a_resource, resource_name):
        self.putChild(resource_name, a_resource)
        
    def getChild(self, name, request):
        try:            
            return(TestResource(rest_simulator.cos[0].ucs[1]))
        except:
            return NoResource() 

        
        
class Scada(RESTfulResource):
    # TODO: Encender el scada
    # TODO: Detener scada
    pass
    
#base_resource = BaseResource()

base_resource= TestBaseResource()
for co in rest_simulator.cos:
    base_resource.add_child(co, 'co/%d'%co.id)
    for uc in co.ucs:
        base_resource.add_child(uc, 'co/%d/uc/%d'%(co.id,uc.id))
rest_simulator.simulate()
site = server.Site(base_resource)





