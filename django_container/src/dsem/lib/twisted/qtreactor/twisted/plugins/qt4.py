# Copyright (c) 2001-2007 Twisted Matrix Laboratories.
# This file is licensed under GPLv2


from twisted.application.reactors import Reactor

qt4 = Reactor('qt4', 'qt4reactor', 'Qt4 integration reactor')
qt4bad = Reactor('qt4bad', 'qt4reactor_bad', 'Qt4 broken reactor')

