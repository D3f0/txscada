#! /usr/bin/env python
# -*- encoding: utf-8 -*-


import sys
#from PyQt4 import QtCore, QtGui
import ho.pisa as pisa
import cStringIO as StringIO
import logging
from jinja2 import *


def main(argv = sys.argv):
    
    fp = open('template.html')
    template = fp.read()
    fp.close()
    template = Template(template)
    datos = range(100)
    salida_template = template.render(datos = datos)
    salida_archivo = open('resultado.pdf', 'w')
    pdf = pisa.pisaDocument(salida_template.encode("UTF-8"), salida_archivo)
    if pdf:
        print "OK"
        
    salida_archivo.close()
    


if __name__ == "__main__":
    sys.exit(main())