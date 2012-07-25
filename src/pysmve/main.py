#!/usr/bin/env python2
# encoding: utf-8

import sys
import utils
import errors
print utils


def runcommand(cmdline, options, command_dict):
    """Split commands in fabric style,
    returns (cmdname, cmdkwargs)"""
    if ':' in cmdline:
        cmdname, args = cmdline.split(':', 1)
    else:
        cmdname, args = cmdline, ''
    #print cmdname, "-", args
    command_name = utils.choose(cmdname, command_dict.keys())

    name = command_name        
    command_func = command_dict[name]
    try:
        kwargs = utils.make_kwargs(command_func, args)
    except ValueError as e:
        raise errors.CommandArgumentError(unicode(e))
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
    except errors.CommandArgumentError as e:
        print "Command Argument Error: %s" % e
    return -1
        
    
    


if __name__ == "__main__":
    sys.exit(main())