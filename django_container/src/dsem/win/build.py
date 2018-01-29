#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
A very simple script to automate the building process under windows
'''

import os, sys, shutil
try:
    import py2exe
except ImportError:
    print "You doon't seem to have py2exe installed."
    sys.exit(-3)

    
print "Checking directory"
cur_dir = os.getcwd().split(os.sep)[-1]
if cur_dir != 'win':
    sys.stderr.write("You're not at the top of the project folder hierachy")
    sys.exit(-1)

print "Deleting previous build files"
shutil.rmtree('build', True)
shutil.rmtree('win32', True)

print "*** UPDATING ***"
os.system('hg pull -u')

print "*** BUILDING ***"
os.system('python -OO setup.py py2exe')