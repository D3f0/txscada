from fabric.api import *

DEV_REQUIEREMENTS_FILE = 'requirements/develop.txt'

def freeze():
    '''Freezar los requerimientos del virtualenv'''
    with open(DEV_REQUIEREMENTS_FILE, 'wb') as f:    
        reqs = local('pip freeze', True)
        f.write(reqs)
    print "Requirements written to %s" % DEV_REQUIEREMENTS_FILE
        
    