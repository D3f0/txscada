#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import re, os, sys

def mkpath(*l):
    return os.sep.join(l)

def recursive_datadir_list(dirs, bans = [], strip_up_to = 0):
    def skip(file_name):
        ''' Guess if the file is desired or not '''
        for ptrn in bans:
            if re.search(ptrn, file_name):
                return True
        return False
    file_map = {}
    if type(dirs) == str:
        dirs = [dirs]
    for data_dir in dirs:
        print "*" 
        for dirpath, dirnames, filenames in os.walk(data_dir):
            if skip(dirpath):
                continue
            if len(filenames) == 0:
                continue
            files = [ os.path.join(dirpath, f) for f in filenames if not skip(f) ]
            if strip_up_to:
                name = dirpath.strip(os.sep).split(os.sep)[strip_up_to:]
                name = os.sep.join(name)
            else:
                name = dirpath
            file_map[name] = files
    return file_map.items()

def recursive_module_list(name, bans = [], full_search = False):
    bans.append('.svn')
    bans.append('.hg')
    path, module, modules = None, None, []
    try:
        module = __import__(name, {}, {}, ['*'])
        path = getattr(module, '__path__')
    except ImportError:
        print "Error de importacion", name
        return None
    path = path[0]
    base = os.path.abspath(os.path.join(path, '..'))
    print "Asumiendo el directorio '%s' para '%s'" % (path, name)
    for dirpath, dirnames, filenames in os.walk(path):

        for ban in bans:
            if ban in dirpath.split(os.sep):
                continue

        if '__init__.py' in filenames:
            mod = dirpath.replace(base, '').replace(os.sep, '.')[1:]
            modules.append(mod)
            if full_search:
                filenames.pop(filenames.index('__init__.py'))
                py_files = filter(lambda x: x.endswith('.py'), filenames)
                extra_mod = [ mod + '.' + f.replace('.py','') for f in py_files]
                for x in extra_mod:
                    modules.append(x)
    return modules

def recurive_module_sub_dir(modules, sub_dir, bans =  ['.hg', '.svn',]):
    ''' Para agrear los templates de las aplicaciones de django.
    No podemos hacer un __import__('django.contrib.admin'...) porque
    al no tener un settings definido, no funciona'''
    if type(modules) not in [list, tuple]:
        modules = [modules, ]
    for module in modules:
#        print module
        outermost = module.split('.')[0]
        print outermost
        try:
            mod = __import__(outermost, {}, {}, ['*'])
        except ImportError, e:
            print e
            continue
        else:
            base_path = mod.__path__
            full_slices = base_path + module.split('.')[1:] + [ sub_dir ]
#            print full_slices
            full = os.sep.join(full_slices)
            if os.path.exists(full):
                name = module.split('.')[-1]
                
                index = full.strip(os.sep).split(os.sep).index(name)
                return recursive_datadir_list([full], bans, index + 1)
        
def main(argv = sys.argv):
    ''' Quick Testing '''
    from pprint import pprint
    data = recursive_datadir_list(mkpath('winlauncher','res'), ['README'], 1)
    pprint(data)
    data = recursive_module_list('dscada', full_search = True)
    pprint(data)
    apps = [ 'django.contrib.databrowse' ]
    pprint(recurive_module_sub_dir(apps, 'templates'))
    
if __name__ == '__main__':
    sys.exit(main())