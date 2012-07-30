import re

def ints_from_str(hexstr):
    '''Takes ints from hexstring'''
    parts = re.split(r'[\s:\t]', hexstr) 
    for part in filter(len, parts):
        yield int(part, 16)
        

if __name__ == '__main__':
    print list(ints_from_str('FE    08    01    40    80    10    80    A7'))