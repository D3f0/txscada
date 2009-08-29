'''
Created on 29/08/2009

@author: defo, lau
'''

from twisted.web import server
from twisted.web import resource

class BaseResource( resource.Resource ):
    pass

base_resource = BaseResource()

site = server.Site( base_resource )


