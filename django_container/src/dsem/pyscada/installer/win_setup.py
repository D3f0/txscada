#! /usr/bin/env python
# coding: utf-8
 
 
'''
Instalador en windows.
Instalación de la DB como servicio.
'''
import os, sys
import re
from pprint import pformat
import commands
from ConfigParser import ConfigParser

# Sacado de Django
class SortedDict(dict):
    """
    A dictionary that keeps its keys in the order in which they're inserted.
    """
    def __init__(self, data=None):
        if data is None:
            data = {}
        super(SortedDict, self).__init__(data)
        if isinstance(data, dict):
            self.keyOrder = data.keys()
        else:
            self.keyOrder = []
            for key, value in data:
                if key not in self.keyOrder:
                    self.keyOrder.append(key)

    def __deepcopy__(self, memo):
        from copy import deepcopy
        return self.__class__([(key, deepcopy(value, memo))
                               for key, value in self.iteritems()])

    def __setitem__(self, key, value):
        super(SortedDict, self).__setitem__(key, value)
        if key not in self.keyOrder:
            self.keyOrder.append(key)

    def __delitem__(self, key):
        super(SortedDict, self).__delitem__(key)
        self.keyOrder.remove(key)

    def __iter__(self):
        for k in self.keyOrder:
            yield k

    def pop(self, k, *args):
        result = super(SortedDict, self).pop(k, *args)
        try:
            self.keyOrder.remove(k)
        except ValueError:
            # Key wasn't in the dictionary in the first place. No problem.
            pass
        return result

    def popitem(self):
        result = super(SortedDict, self).popitem()
        self.keyOrder.remove(result[0])
        return result

    def items(self):
        return zip(self.keyOrder, self.values())

    def iteritems(self):
        for key in self.keyOrder:
            yield key, super(SortedDict, self).__getitem__(key)

    def keys(self):
        return self.keyOrder[:]

    def iterkeys(self):
        return iter(self.keyOrder)

    def values(self):
        return [super(SortedDict, self).__getitem__(k) for k in self.keyOrder]

    def itervalues(self):
        for key in self.keyOrder:
            yield super(SortedDict, self).__getitem__(key)

    def update(self, dict_):
        for k, v in dict_.items():
            self.__setitem__(k, v)

    def setdefault(self, key, default):
        if key not in self.keyOrder:
            self.keyOrder.append(key)
        return super(SortedDict, self).setdefault(key, default)

    def value_for_index(self, index):
        """Returns the value of the item at the given zero-based index."""
        return self[self.keyOrder[index]]

    def insert(self, index, key, value):
        """Inserts the key, value pair before the item with the given index."""
        if key in self.keyOrder:
            n = self.keyOrder.index(key)
            del self.keyOrder[n]
            if n < index:
                index -= 1
        self.keyOrder.insert(index, key)
        super(SortedDict, self).__setitem__(key, value)

    def copy(self):
        """Returns a copy of this object."""
        # This way of initializing the copy means it works for subclasses, too.
        obj = self.__class__(self)
        obj.keyOrder = self.keyOrder[:]
        return obj

    def __repr__(self):
        """
        Replaces the normal dict.__repr__ with a version that returns the keys
        in their sorted order.
        """
        return '{%s}' % ', '.join(['%r: %r' % (k, v) for k, v in self.items()])

    def clear(self):
        super(SortedDict, self).clear()
        self.keyOrder = []




class IniParser(object):
    '''
    A simple lousy ini file parser and saver
    '''
    SECTCRE = re.compile(
        r'\['                                 # [
        r'(?P<header>[^]]+)'                  # very permissive!
        r'\]'                                 # ]
        )
    OPTCRE = re.compile(
        r'(?P<option>[^:=\s][^:=]*)'          # very permissive!
        r'\s*(?P<vi>[:=])\s*'                 # any number of space/tab,
                                              # followed by separator
                                              # (either : or =), followed
                                              # by any # space/tab
        r'(?P<value>.*)$'                     # everything up to eol
        )
    
    
    COMMENT_START = '#;'

    def __init__(self, name = None):
        self._data = SortedDict()
        self._f_name = name
        self._fp = open(self._f_name, 'r')
        self._do_parse()
        self._fp.close()
        
        
    def _do_parse(self):
        current_section, current_dict = None, None
        for n, line in enumerate(self._fp.readlines()):
            line = line.strip()
            if len(line) < 2 or line[0] in IniParser.COMMENT_START:
                # skip empty lines, and comments
                continue
            
            match = IniParser.SECTCRE.search( line )
            if match:
                current_section = match.group('header')
                if not self._data.has_key( current_section ):
                    current_dict = self._data[ current_section ] = SortedDict()
                else:
                    current_dict = self._data[ current_section ]
                continue
            match = IniParser.OPTCRE.search( line )
            if match:
                key, val = match.group('option').strip(), match.group('value').strip()
                current_dict [ key ] = val
                continue
            # Everything that doesn't look like an option, might be some 
            # kind of flag
            current_dict[ line ] = None
    
    def set_value(self, section, option, value):
        if not self._data.has_key(section):
            raise ValueError("This file doesn't have any «%s» section.")
        self._data[section][option] = value
        
    def save(self, name = None):
        fp = open(name or self._f_name, 'w+')
        for key in self._data.keys():
            fp.write('[%s]\n' % key)
            for k, v in self._data[ key ].iteritems():
                if v:
                    fp.write(r'%s = %s\n' % (k, v))
                else:
                    fp.write('%s\n' % k)
                fp.write('\n')
        fp.close()
    
    def __str__(self):
        return pformat(self._data)
    
if __name__ == "__main__":
    #parser = ConfigParser()
    #parser.addOption('-m', '--mysql-dir')
    try:
        ini = IniParser('my.ini')
        ini.set_value('mysqld', 'datadir', 'c:\\\\pepe\\\\foo')
        ini.save('prueba.ini')
    except IOError:
        sys.exit(2)
    
