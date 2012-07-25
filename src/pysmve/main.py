#!/usr/bin/env python2
# encoding: utf-8

import sys
import utils
import errors
print utils


def runcommand(cmdline, options, command_dict):
    """Split commands in fabric style,
    returns (cmdname, cmdkwargs)"""
    from difflib import get_close_matches
    if ':' in cmdline:
        cmdname, args = cmdline.split(':', 1)
    else:
        cmdname, args = cmdline, ''
    #print cmdname, "-", args
    command_name = get_close_matches(cmdname, command_dict.keys())
    n = len(command_name)
    if n == 0:
        raise errors.NoSuchCommand("No command named %s" % cmdname)
    else:
        name = command_name[0]
        if n > 1:
            print "Choosing %s from %s" % (name, ', '.join(command_name))
        command_func = command_dict[command_name[0]]
        
    kwargs = utils.make_kwargs(command_func, args)
    return command_func(options, **kwargs)
    


def main(argv = sys.argv):
    # Aplicación
    
    from commands import COMMANDS
    from options import parser
    
    options = parser.parse_args()
    try:
        return runcommand(options.command[0], options, command_dict=COMMANDS)
    except errors.NoSuchCommand as e:
        print e
        return -1
    
    


if __name__ == "__main__":
    sys.exit(main())