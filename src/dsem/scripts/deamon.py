#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
from os.path import isfile 
sys.path.insert(0, '..')
from imp import find_module, load_module
from optparse import OptionParser
from scada import scada_main_cli

def load_django_settings(path):
    if not isfile(path):
        raise Exception("No existe el archivo %s" % path)
    if path.endswith('.py'):
        path = path.replace('.py', '')
    try:
        set_mod_tup = find_module(path)
        return load_module('settings', *set_mod_tup)
    except ImportError, e:
        raise Exception("No se puede cargar el modulo %s" % path)

def main(argv = sys.argv):
    '''
    Punto de entrada al programa
    '''
    parser = OptionParser(description = u"Servidor de adquisicion de datos")
    parser.add_option("-s", "--settings", dest="settings", type=str, help=u"Modulo de configuración django",
                        default='../dscada/settings.py')
    parser.add_option("-p", "--xh_port", dest="xh_port", type=str, help=u"Puerto para el servidor XmlHttp")
    parser.add_option("-i", "--xh_iface", dest="xh_iface", type=str, help=u"Interfase para el servidor XmlHttp")
    parser.add_option("-o", "--only", dest="con", type="str", help=u"Concetrador al cual hacer consultas, dejando de lado el resto")
    parser.add_option("-x", "--exclude", dest="exc", type="str", help=u"Concetrador al cual ignorar al hacer consultas")
    #TODO: Implementar esto
    parser.add_option("-c", "--config", dest="config", type=str, help=u"Archivo de configuracion del demonio")
    # Parseamos al entrada de usuario
    (options, args) = parser.parse_args(argv)
    
    if not options.settings:
        print "Asumiendo settings.py en el mismo directorio..."
        options.settings = 'settings.py'
    options.xh_port = options.xh_port or 6000
    options.xh_iface = options.xh_iface or "127.0.0.1"
    settings = load_django_settings(options.settings)
    
    print "Arrancando SCADA..."
    try:
        scada_main_cli(options, settings)
    except (KeyboardInterrupt, EOFError):
        print "Terminado"
        

if __name__ == '__main__':
    sys.exit(main())