# encoding: utf-8
import re
from werkzeug.datastructures import CombinedMultiDict
def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# -------------------------------------------------------------
# Conversion de tipos de acuerdo con el nombre
# -------------------------------------------------------------
DATATYPES = {
    'b': lambda d: d.upper() == True,
    'i': int,
    'f': float,
    's': unicode,
}

def parseparams(request_values):
    
    
    d = {}
    for name, val in request_values.items():
        typeinfo = name[:1] 
        if typeinfo in DATATYPES:
            func = DATATYPES[typeinfo]
            d[convert(name[1:])]= func(val)
    return d
    
