#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
import pprint
import html_render
import threading
import random
import time

BASE_PATH = os.getcwd()+'/static'


class Concentrador(object):
    """ Emula un concentrador """
    
    def __init__ (self,id):
        """ Class initialiser """
        path = BASE_PATH + '/cos/co_%d'%id
        #self.f = open(path,'rw')
        self.id = id
        self.ucs = []
        
    def agregar_uc(self, uc):
        self.ucs.append(uc)
        
    def eliminar_uc(self,uc):
        if not isinstance(uc, int):
            idx = self.ucs.index(uc)
        else:
            idx = uc
        self.ucs.remove(idx)
    
    def __str__(self):
            """ Function doc
        
            @param PARAM: DESCRIPTION
            @return RETURN: DESCRIPTION
            """
            ucs = pprint.pformat([str(uc) for uc in self.ucs])
            return 'Co %d - %s' %(self.id, ucs)
    #__repr__ = __str__
    
    
    def register(self):
        s = '/co/%d' %self.id        
        for uc in self.ucs:
            for t, ref in uc.register():
                yield (s + t, ref)
        yield (s, self)

        
class Unidad_de_Control(object):
    """ Emula una unidad de control """
    
    def __init__ (self,id):
        """ Class initialiser """
        path = BASE_PATH + '/ucs/uc_%d'%id
        #self.f = open(path,'rw')
        self.id = id
        self.data = {}
        
        
    def add_ai(self, ai_id):
        self.data['ai%d' %ai_id] = 0
        
    def add_di(self, di_id):
        self.data['di%d' %di_id] = 0
        
        
    def do_something(self):        
        for k in self.data.keys():
            if k.startswith('ai'):
                self.data[k] = self.data[k] = random.random()
            elif k.startswith('di'):
                self.data[k] = random.randint(0, 255)
       
    def __str__(self):
        """ Function doc
    
        @param PARAM: DESCRIPTION
        @return RETURN: DESCRIPTION
        """        
        s1 = 'Uc %d' %self.id
        s2 = pprint.pformat(self.data)
        return '\n'.join([s1, s2])
        
    

    #__repr__ = __str__
    
    def register(self):
        s = '/uc/%d' %self.id
        yield (s, self)
    
    

def make_html(an_object):
    h = html.HTML()
    head = h.head()
    head.title("testing! " + str(type(an_object)))
    body = h.body()
    body.h1(str(type(an_object)))
    body.p(str(an_object))
    return str(h)


def foo(un_co):
    for uc in un_co.ucs:
        uc.do_something()
#        print uc
        

def bar(lst):
#    while True:
    for _ in xrange(10):
        for co in lst:
            foo(co)
        time.sleep(5)


def simulate():
    t = threading.Thread(target=bar, args=(cos,))
    t.start()    
    
    


cos = []
for i in xrange(2):
    cos.append(Concentrador(i))
ucs = []
for i in xrange(10):
    uc = Unidad_de_Control(i)
    if i < 5:
        cos[0].agregar_uc(uc)            
    else:
        cos[1].agregar_uc(uc)            
    ucs.append(uc)
    uc.add_ai(1)
    uc.add_di(1)
    
def get_paths():
    for uc in ucs:
        for s,ref in uc.register():
            yield (s,ref)



if __name__ == '__main__':
    
    
    cos = []
    for i in xrange(2):
        cos.append(Concentrador(i))
    ucs = []
    for i in xrange(10):
        uc = Unidad_de_Control(i)
        if i < 5:
            cos[0].agregar_uc(uc)            
        else:
            cos[1].agregar_uc(uc)            
        ucs.append(uc)
        uc.add_ai(1)
        uc.add_di(1)
    
####    t = threading.Thread(target=bar, args=(cos,))
##    t.start()
    d = {}
    for a,b in get_paths():
        d[a] = b
    print d.keys()
    print d.values()
    print type(d.values()[0])
