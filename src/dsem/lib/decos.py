#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from time import time



class timeit(object):
    ''' Decorador para la medicion del tiempo '''
    
    def __init__(self, name = None):
        self.name = name or 'funcion'
    
    def __call__(self, f):
        def wrapped(*largs, **kwargs):
            time0 = time()
            retval = f(*largs, **kwargs)
            ftime = time() - time0
            fps = float(1) / ftime
            print "Ejecutado %s en %.7f AVG FPS: %.3f" % (self.name, ftime, fps)
            return retval
        return wrapped
    