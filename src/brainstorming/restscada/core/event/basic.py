#!/usr/bin/env python
#-*- encoding: utf-8 -*-
# Created: 17/12/2009 by defo

'''
Broadcast de eventos.
# <---------
picnet_v1.co.1.uc.1.di_data
picnet_v1.co.1.uc.1.ai_data
picnet_v1.co.1.uc.1.st_data
picnet_v1.co.1.uc.1.ev_data

# -------------->
picnet_v1.co.1.uc.1.cmd
picnet_v1.co.1.uc.1.cmd


# Por REST
/picnet_v1/co/1/uc/1/cmd POST

'''

class Event(object):
    _name, _value = None, None
    def __init__(self, name, payload = None):
        self.name =  name
        self.payload = payload or {}
        
    def payload(): #@NoSelf
        def fget(self):
            return self._payload
        def fset(self, value):
            assert issubclass(type(value), dict)
            self._payload = value
        return locals()
    payload =  property(**locals())
    
    def name(): #@NoSelf
        def fget(self):
            return self._name
        def fset(self, value):
            self._name = value
            
            
def emit(name, values):
    None
    


    
    