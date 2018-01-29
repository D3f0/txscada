#!/usr/bin/env python
# encoding: utf-8
'''
Servidor Web que publica los recursos REST.
'''
import sys
from twisted.internet import reactor
try:
    from config import Config
except ImportError:
    print "No se encuentra el módulo de configuración 'config'"
    print "Por favor instalelo desde 'http://pypi.python.org/pypi/config/0.3.7'"
    print "o mediante la orden easy_install config"
    print "si posee pip (reemplazo sugerido de easy_install), realize pip install config"
    sys.exit(-2)

class activate_on(object):
    def __init__(self, message_name):
        pass
    
    def __call__(self, f):
        def wrapped(*largs, **kwargs):
            val = f(*largs, **kwargs)
            return val
        

class PicnetPoller(object):
    
    @activete_on('picnet.poll.start')
    def start_timer(self):
        reactor.callLater(cfg.picnet.poll_time, self.do_poll)
        
    
    @activate_on('picnet.poll.stop')
    def stop_timer(self):
        pass
    
    def do_poll(self):
        pass
    
print "hola"
    