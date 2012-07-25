#!/usr/bin/env python2
# encoding: utf-8

import sys
from functools import partial
import inspect
from copy import copy


def coincidence(s1, s2):
    counter = 0
    for c1, c2 in zip(s1, s2):
        if not c1 == c2: break
        counter += 1
    return counter

def choose(ref, names):    
    coincidences = map(lambda s: coincidence(ref, s), names)
    return names[coincidences.index(max(coincidences))]
    
def choose_pop(starting, listofargs):
    '''
    Removes most similar word from listofargs with startswith(starting)
    criteria.
    Ex: choose_pop('ab', ['abc', 'def']) => returns abc, listofargs ['def']
    '''
    coincidences = map(lambda s: coincidence(starting, s), listofargs)
    mostlikely = max(coincidences)
    if not mostlikely:
        raise ValueError("Argument error with %s" % starting)
    index = coincidences.index(mostlikely) # Most likely word maximises
    value = listofargs.pop(index)
    return value
    
    
def make_kwargs(func, strofargs):
    ''' Geneate kwargs dict based on function argspec'''
    if not strofargs: return {}
    
    argspec = inspect.getargspec(func)
    args = copy(argspec.args[1:]) # Options is always the first argument
    kwargs = {}
    parts = strofargs.split(':')
    for arg in parts:
        if not len(arg): continue
        if '=' in arg:
            k, v = arg.split('=')
        else:
            k, v = (arg, arg)
    
    kwargs.update({choose_pop(k, args): v})
    return kwargs

def runcommand(cmdline, options, command_dict):
    """Split commands in fabric style,
    returns (cmdname, cmdkwargs)"""
    from difflib import get_close_matches
    if ':' in cmdline:
        cmdname, args = cmdline.split(':', 1)
    else:
        cmdname, args = cmdline, ''
    print cmdname, "-", args
    command_name = get_close_matches(cmdname, command_dict.keys())
    n = len(command_name)
    if n == 0:
        raise KeyError("No command named %s" % cmdname)
    else:
        name = command_name[0]
        if n > 1:
            print "Choosing %s from %s" % (name, ', '.join(command_name))
        
        command_func = command_dict[command_name[0]]
    kwargs = make_kwargs(command_func, args)
    print kwargs
    return command_func(options, **kwargs)
    
    
        
    
    

def main(argv = sys.argv):
    # Aplicación
    
    from commands import COMMANDS
    from options import parser
    
    options = parser.parse_args()
    try:
        return runcommand(options.command[0], options, command_dict=COMMANDS)
    except Exception as e:
        print e
        from traceback import format_exc
        print format_exc()
        return -1
    
    


if __name__ == "__main__":
    sys.exit(main())