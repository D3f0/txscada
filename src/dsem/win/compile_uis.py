#! /usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Cansado de pelear con el GNU Make, es más sencillo
crear mi propio compilador de uis
'''

import os
import re
import copy
from subprocess import Popen, PIPE

find = lambda name: os.popen("which %s" % name).read().strip()
 
RULES = {'uis':
             {
                'file_pattern': r'(?P<fname>[\w\d_]+)\.[Uu][Ii]$',
                'target_pattern': u'%(fpath)s/../ui_%(fname)s.py',
                'exec' : find('pyuic4') or find('pyuic'),
                'command': '%(exec)s %(source)s -o %(target)s',
                'on_error': 'rm %(target)s',
              },
         }

def get_files(root = '.'):
    ''' Obtiene los archivos de una ruta, por defecto el directorio acutal'''
    files = []
    for dirpath, _, filenames in os.walk(root):
        for file in filenames:
            name = os.path.join(dirpath, file)
            files.append(os.path.abspath(name))
    return files
        
def compare_dates(first, second):
    '''
    @precondition: El archivo first debe existir
    '''
    if not os.path.exists(second):
        return True
    if os.path.getmtime(first) > os.path.getmtime(second):
        return True
    return False
        
def process_rules(rules):
    ''' Procesar reglas, cada regla es un diccionario '''
    for rule_name in rules:
        print "Processing rule %s" % rule_name
        rule = rules.get(rule_name)
        file_pattern = rule.get('file_pattern', None)
        
        assert file_pattern is not None, u"The  '%s' rule has no file_pattern" % rule_name
        # TODO: Este script se puede estar corriendo desde otro path
        base = rule.get('base', '.')
        files = get_files(root = base)
        on_error = rule.get('on_error', None)
        
        for file in files:
            match = re.search(file_pattern, file, re.UNICODE)
            if not match:
                continue
            replace_dict = match.groupdict()
            # Nos guardamos el nombre completo del archvo que matcheó
            replace_dict.update(source = file)
            # Path
            replace_dict.update(fpath = os.path.dirname(os.path.abspath(file)))
            replace_dict.update(rule)
            # Si exite patrón destino
            target_pattern = rule.get('target_pattern', False)
            # Inicializamos la variable
            replace_dict['target'] = None
            # Ahora reemplazamos el patrón
            if target_pattern:
                target = os.path.abspath(target_pattern % replace_dict)
                if not target.startswith('/'):
                    target = os.path.join(os.path.dirname(file), target)
                    print "*"
                replace_dict['target'] = target
            command = rule.get('command', False)
            assert command, "No command for rule %s" % rule_name

            if compare_dates(replace_dict['source'], replace_dict['target']):
                command = command % replace_dict
                proc = Popen(command.split(), stdout=PIPE, stderr=PIPE)
                if proc.wait() != 0:
                    print "*** Error en %s ***" % command
                    if on_error:
                        os.popen(on_error % replace_dict)
                    
            else:
                print replace_dict['source'], 'is up to date'
def main():
    # TODO: Mostrar más información
    print "My Simple Chained Make taking control"
    process_rules(RULES)
    print "All done"
    
if __name__ == '__main__':
    main()