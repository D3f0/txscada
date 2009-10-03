'''
Created on 03/10/2009

@author: defo
'''

from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log
from config import Config
import sys


class Root(resource.Resource):
    def render_GET(self, request):
        return "Probaste en <a href='data'>/data/?</data>?"

class TestReource(resource.Resource):
    def render_GET(self, request):
        return "Hola"
    
def main(argv = sys.argv):
    log.startLogging(sys.stderr, setStdout = False)
    cfg = Config(open('config.cfg'))
    root = Root()
    root.putChild( 'data', TestReource() )
    site = server.Site(root)
    
    reactor.listenTCP(cfg.webserver.port, site)
    reactor.run()

if __name__ == "__main__":
    
    main()



