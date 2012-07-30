import re

def ints_from_str(hexstr):
    '''Takes ints from hexstring'''
    for s in re.finditer('[\s:]', hexstr, re.IGNORECASE):
        yield int(s, 16)