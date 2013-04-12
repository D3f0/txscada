import functools
from time import sleep

def prepeare(signals=[]):
    def decorator(function):
        @functools.wraps(function)
        def f(*args, **kwargs):
            for sig in signals:
                print sig
            return function(*args, **kwargs)
        return f
    return decorator



@prepeare(['a', 'b'])
def foo():
    print "FOO"



print "A"
foo()