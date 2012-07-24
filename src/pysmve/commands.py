# Comandos para el main


import functools
import exceptions

COMMANDS = {}

def command(obj):
    global COMMANDS
    if not callable(obj):
        raise exceptions.ImproperlyConfigured("Task should be callable objects")
    
    
    @functools.wraps(obj)
    def wrapped(*largs, **kwargs):
        # ------------------------------------------------------------
        # Run command in context
        # ------------------------------------------------------------
        return obj(*largs, **kwargs)
    COMMANDS[obj.func_name] = obj
    return wrapped
    
    
@command
def server(options):
    print "server"
    
@command
def dbshell(options):
    print "dbshell"
    


if __name__ == '__main__':
    # Print available commands
    print COMMANDS.keys()

    
    
