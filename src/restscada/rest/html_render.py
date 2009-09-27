#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Utilidades para renderizar objetos a HTML
Podría verse como un simple motor de templates
'''

import html
import pprint


def list_to_html(iterable):
    h = html.HTML()
    lst = h.ul()
    for el in iterable:
        #lst.li(to_html(el))
        itm = lst.li()       
        itm.raw_text(to_html(el))
    return h
        
def dict_to_html(dictionary):
    '''
    No usar hasta no saber cómo arreglar la cuestión de orden en las keys 
    de los diccionarios
    '''
    h = html.HTML()    
    for k, v in dictionary.iteritems():
        e = h.__getattr__(k)
        e.raw_text(str(v))        
    return h


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
