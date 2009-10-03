'''
Created on 03/10/2009

@author: defo
'''
#coding: utf8
from twisted.internet import reactor, defer
from twisted.web.client import getPage
from twisted.python.util import println
from twisted.python import log
from config import Config
import sys
import time



def data_retrival_error(e):
    
    map(log.err, [
                  "ERRROR",
                  e,
                  "Dying :'(",
                  ])
    reactor.stop()

def poll_data(url, delay = 0.0, on_update = None):
    def handle_data(data):
        if callable(on_update):
            return on_update(data)
        return data
    
    d = getPage(url).addErrback(data_retrival_error)
    d.addCallback(handle_data)
    d.addCallback(lambda _: reactor.callLater(delay, poll_data,
                                                # Args 
                                                url, delay, on_update)).addErrback(println)
    
    
def main(argv = sys.argv):
    log.startLogging(sys.stderr, setStdout = False)
    cfg = Config('config.cfg')
    poll_data('http://localhost:%d/data' % cfg.webserver.port, delay = 0.1, on_update = log.msg)
    
    reactor.run()
    
if __name__ == '__main__':
    main()