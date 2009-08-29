#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
import pprint

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
    
    def __str__(self):
            """ Function doc
        
            @param PARAM: DESCRIPTION
            @return RETURN: DESCRIPTION
            """
            ucs = pprint.pformat([str(uc) for uc in self.ucs])
            return 'Co %d - %s' %(self.id, ucs)
    __repr__ = __str__

        
class Unidad_de_Control(object):
    """ Emula una unidad de control """
    
    def __init__ (self,id):
        """ Class initialiser """
        path = BASE_PATH + '/ucs/uc_%d'%id
        #self.f = open(path,'rw')
        self.id = id
        
    def __str__(self):
        """ Function doc
    
        @param PARAM: DESCRIPTION
        @return RETURN: DESCRIPTION
        """        
        return 'Uc %d' %self.id

    __repr__ = __str__


if __name__ == '__main__':
    
    
    cos = []
    for i in xrange(2):
        cos.append(Concentrador(i))
    ucs = []
    print cos
    for i in xrange(10):
        uc = Unidad_de_Control(i)
        if i < 5:
            cos[0].agregar_uc(uc)
        else:
            cos[1].agregar_uc(uc)            
        ucs.append(uc)
    print BASE_PATH
    index = open(BASE_PATH + '/index.html', 'w')
    index.write('<html><body><p>')
    for co in cos:
        index.write(str(co)+'\n')
    index.write('</p></body></html>')
    index.close()
    
