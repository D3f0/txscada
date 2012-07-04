'''
Created on 06/10/2009

@author: defo
'''
import routes
from routes.middleware import RoutesMiddleware

m = routes.Mapper('controllers')

m.connect('/ucnet/co/:co_id/', controller = 'CO', action = 'controller_list',
          conditions={'methods': ['GET',]})

m.connect('/ucnet/co/:co_id/', controller = 'CO', action = 'controller_create',
          conditions={'methods': ['PUT',]})



print m.match('/ucnet/co/3/')
print m.match('/')
