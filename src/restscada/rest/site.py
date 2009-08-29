'''
Created on 29/08/2009

@author: defo, lau
'''

from twisted.web import server, resource, static


class UserAgentDelegate(object):
    def render(self):
        raise NotImplementedError("You must sublcass this method")

#class HTMLDelegate():

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
        
class Scada(RESTfulResource):
    # TODO: Encender el scada
    # TODO: Detener scada
    pass
    
base_resource = BaseResource()
site = server.Site(base_resource)





