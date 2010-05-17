#! /usr/bin/env python
# -*- encoding: utf-8 -*-


from pprint import pformat
class BinaryStates(object):
    def __init__(self, *largs, **kwargs):
        
        self._states = {}
        if kwargs:
            for k, v in kwargs.iteritems():
                assert self.valid(k), "Clave no permitida '%s'" % k
                assert k not in self._states, "Clave repetida %s" % k
                assert type(v) == int, "Solo se permiten valores enteros %s" % type(v)
                assert v not in self._states.values(), "Valor repetido"
                assert v is not 0, "0 no es un valor legal de estado"
                self._states[k] = v
        if largs:
            cur_val = 1
            for x in largs:
                tokens = []
                x = str(x)
                tokens = filter(lambda x: len(x) > 0,
                                map(lambda s: s.strip(), x.split('\n'))
                            )
                for k in tokens:
                    assert self.valid(k), "Clave no permitida '%s'" % k
                    assert k not in self._states, "Clave repetida %s" % k
                    while cur_val in self._states.values():
                        cur_val <<= 1
                    self._states[k] = cur_val
                    cur_val <<= 1
                
    @classmethod
    def valid(cls, value):
        return value.upper() == value
    
    def __contains__(self, key):
        if type(key) == str:
            return key in self._states
        else:
            return key in self._states.values()
        
    
    def __getattribute__(self, name):
        states = object.__getattribute__(self, '_states')
        if states.has_key(name):
            return states[name]
        return object.__getattribute__(self, name)
        
    def __str__(self):
        return pformat(self._states)
    
# Some tests

if __name__ == "__main__":
    # Define custom states
    States = BinaryStates('''
        ALFA
        BETA
        GAMA
        EPSILONG
        ''',  OMEGA = 32)
    print States
    print 16 in States
    print States.BETA

