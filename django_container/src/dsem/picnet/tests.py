#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import unittest 

class TestPaqutes(unittest.TestCase):

    def testPaquete_procesar(self):
        from proto import Paquete
        from proto import SOF
        from checksum import make_cs_bigendian
        
        p = None
        
        datos = [SOF,
                 0, # Qty
                 1, # Dst
                 2, # Src
                 3, # Sec
                 0, # Com
                 1, # Datos
                 2, # Datos
                 3, # Datos
                 4, # Datos
                 5, # Datos 
                 ]
        
        datos += make_cs_bigendian(datos)
        datos[1] = len(datos) # Qty
        
        p = Paquete.from_int_list(datos)
        print p.d00
        self.assertNotEqual(p.sof, None)
        self.assertNotEqual(p, None)
        
        
    
    
if __name__ == '__main__':
    unittest.main()
    
    