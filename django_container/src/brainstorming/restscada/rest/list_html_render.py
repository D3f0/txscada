#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Súper simple motor de templates, basado en s-expressions

Se define un documento html como una lista anidada, compuesta de 
    tags html o listas de tags.
    
Un tag, o "elemento" es una namedtuple.
Entonces, para crear un documento html simple con un título
y un párrafo es necesario lo siguiente

    >>> # Creamos las namedtuples
    >>> html = make_HtmlTag('html')
    >>> head = make_HtmlTag('head')
    >>> title = make_HtmlTag('title', content='Testing')
    >>> body = make_HtmlTag('body')
    >>> p = make_HtmlTag('p', content='Hola mundo\n')
    >>> # Las ubicamos en una lista
    >>> lst = [html, [head, [title]], [body, [p]]]    
    >>> Echamos a correr el motor
    >>> result = render_list(lst)
    >>> print result

"""

from html import HTML
from collections import namedtuple

HtmlTag = namedtuple('HTMLTag', 'tag id klass style title href src alt content')

def make_HtmlTag(tag, id='', klass='', style='', title='', href='', src='', alt='', content=''):
    return HtmlTag(tag, id, klass, style, title, href, src, alt, content)

    
def anchor(element, h=HTML()):
    h = h.__getattr__(element.tag)(element.content, href=element.href)
    return h

    
def estructural(element, h=HTML()):
    h = h.__getattr__(element.tag)(element.content, 
                                id=element.id, 
                                style=element.style, 
                                klass=element.klass)
    return h


def paragraph(element, h=HTML()):
    h = h.__getattr__(element.tag)(element.content, 
                                id=element.id, 
                                style=element.style, 
                                klass=element.klass)
    return h
    
    
def image(element, h=HTML()):
    h = h.__getattr__(element.tag)(element.content, 
                                src=element.src, 
                                alt=element.alt)
    return h


def separator(element, h=HTML()):
    h = h.__getattr__(element.tag)
    return h
    
    
def default_handler(element, h=HTML()):
    h = h.__getattr__(element.tag)(element.content)
    return h

ent_swch = {
            'a': anchor,
            'table': estructural,
            'img': image,
            'body': estructural,
            'head': estructural,
            'p': paragraph,
            'i': paragraph,
            'b': paragraph,
            'br': paragraph,
            }



def render_list(lst, h=HTML()):
    t = h
    for el in lst:
            if isinstance(el, list):
                render_list(el, t)
            else:    
                f = ent_swch.get(el.tag, default_handler)
                t = f(el, h)               
    return h


if __name__ == '__main__':    
    html = make_HtmlTag('html')
    head = make_HtmlTag('head')
    title = make_HtmlTag('title', content='Testing')
    body = make_HtmlTag('body')
    p = make_HtmlTag('p', content='Hola mundo\n')    
    a = make_HtmlTag('a', href='www.google.com', content='Link a google')
    b = make_HtmlTag('b', content='esto va en negrita\n')
    br = make_HtmlTag('br')
    
    lst = [html, [head, [title]], [body, [p, [a], [b], p]]]    
    result = render_list(lst)
    print str(result)
