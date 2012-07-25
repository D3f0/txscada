from functools import partial
import inspect
from copy import copy
import errors


def coincidence(s1, s2):
    counter = 0
    for c1, c2 in zip(s1, s2):
        if not c1 == c2: break
        counter += 1
    return counter
    
def choose(starting, listofargs, pop=False):
    '''
    Removes most similar word from listofargs with startswith(starting)
    criteria.
    Ex: choose('ab', ['abc', 'def']) => returns abc, listofargs ['def']
    '''
    coincidences = map(lambda s: coincidence(starting, s), listofargs)
    mostlikely = max(coincidences)
    if not mostlikely:
        raise ValueError("Unexpected %s" % starting)
    index = coincidences.index(mostlikely) # Most likely word maximises
    if pop:
        value = listofargs.pop(index)
    else:
        value = listofargs[index]
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
    
    kwargs.update({choose(k, args, pop=True): v})
    return kwargs 
