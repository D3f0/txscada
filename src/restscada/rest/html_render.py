#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Utilidades para renderizar objetos a HTML
Podría verse como un simple motor de templates
'''

import html
import pprint
import OrderedDict


def table_to_html (table, enclose=False):
    """ Recibe una lista de listas y crea una tabla en html
    El sentido es filas-columnas    
    El código devuelto no está encerrado en los tags <table></table> salvo que 
        enclose sea True
    """
    h = html.HTML()
    table_tag = enclose and h.table or h             
    for row in table:
        tr = table_tag.tr
        for col in row:
            td = tr.td
            td.raw_text(to_html(col))    
    return h


def list_to_html(iterable, enclose=False):
    h = html.HTML()
    lst = enclose and h.ul or h
    for el in iterable:
        #lst.li(to_html(el))
        itm = lst.li()       
        itm.raw_text(to_html(el))
    return h
        
def dict_to_html(dictionary):
    '''
    Recibe un OrderedDict cuyas claves son la etiqueta a aplicar al valor.
    Por ejemplo
    from OrderedDict import OrderedDict
    d = OrderedDict()
    d['h1'] = 'Hola'
    d['p'] = 'mundo'
    str(dict_to_html(d)) # <h1>hola</h1>\n<p>mundo</p>
    
    En caso de recibir un diccionario común, no se puede asegurar el orden
        en el que serán impresos los valores    
    '''
    h = html.HTML()    
    for k, v in dictionary.iteritems():
        e = h.__getattr__(k)
        e.raw_text(str(v))        
    return h


def foo (iterable, h=html.HTML()):
    for tag, data in iterable:
        if tag == 'list':
            l = h.ul
            l.raw_text(list_to_html(data))
        elif tag == 'table':
            t = h.table
            t.raw_text(table_to_html(data))
        else:
            e = h.__getattr__(tag)
            #e.raw_text(to_html(v))
            e.raw_text(str(v))

def to_html(obj):
    h = html.HTML()
    if isinstance(obj, list):
        return list_to_html(obj)
    elif isinstance(obj, dict):
        return dict_to_html(obj)
    else:        
        p = h.p('')
        p.text(str(obj))
        return h
            


def html_page(title=None, data=None):
    h = html.HTML()
    head = h.head
    if title:
        head.title(title)
    body = h.body
    if data:
        body.raw_text(to_html(data))
    else:
        body.text('')
    return str(h)


def co_render (a_co):
    """ 
    Transforma un concentador en un OrderedDict para luego ser 
    convertido en html 
    """
    d = OrderedDict.OrderedDict()
    d['h1'] = 'Concentrador %d' %co.id
    d['']
