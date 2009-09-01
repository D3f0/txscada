#!/usr/bin/env python
# enconding: utf-8
'''
Un resolvedor de urls similar al de django.
'''

#from restscada.utils.datatypes import namedtuple

class BadURLException(Exception):
    pass

class URLEntry(object):
    def __init__(self, url, dest, opts = None):
        pass
    
class URLResolver(object):
    def __init__(self, patterns):
        self.patterns = patterns
    
    def resolve(self, request):
        pass
    

    
def build_urls(*url_list):
    '''
    * url_list *
        Lista de urls con los siguientes campos
        * url *
            Expresión regular
        * dest *
            Una función o una clase que acepta __call__, los grupos nombrados tomados
            de la url se traducen en parametros reales de la función.
        * opts *
            Parametos extra a ser evaluados
    '''
    try:
        url_entries = map(lambda t: URLEntry(*t), url_list)
    except Exception, e:
        raise BadURLException()
    
    return URLResolver(url_entries)

    
if __name__ == "__main__":
    
    def create_co(request, *largs):
        print "Create CO"
        
    urls = build_urls(
        (r'^/co/(?P<co_id>\d)/$', create_co),
                      
    )
    