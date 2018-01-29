# coding: utf-8

ROTATION = 13
def rstring(string, rotate = ROTATION):
    output = ''
    for i, c in enumerate(string):  
        byte = ord(c)  
        for k in range(0, rotate):  
            byte += 1  
            if byte > 122:  
                byte = 97  
            elif byte > 90 and byte < 97:  
                byte = 65  
        output = '%s%s' % (output, chr(byte))
    return output
            
if __name__ == "__main__":
    print "Prueba de rotacion %d" % ROTATION 
    print 'admin:\t', rstring('admin')
    print 'super:\t', rstring('super')
    print 'oper:\t', rstring('oper')

