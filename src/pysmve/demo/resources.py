from twisted.web import resource
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource

class Root( resource.Resource ):
    """Root resource that combines the two sites/entry points"""

    def __init__(self, app):
    	resource.Resource.__init__(self)
    	self.wsgi = WSGIResource(reactor, reactor.getThreadPool(), app)

    def getChild( self, child, request ):
        # request.isLeaf = True
        request.prepath.pop()
        request.postpath.insert(0,child)
        return self.wsgi

    def render( self, request ):
        """Delegate to the WSGI resource"""
        return self.wsgi.render( request )

def _build_site():
    '''Lazy site initialization for site'''
    # Lazy is needed to prevent greedyness event-loop issues

    from twisted.application import internet, service
    from twisted.web.server import Site
    from twisted.web.static import File
    from twisted.web.wsgi import WSGIResource
    from app import app
    resource = Root(app)
    resource.putChild('static', File('static'))
    site = Site(resource)
    return site

site = _build_site()