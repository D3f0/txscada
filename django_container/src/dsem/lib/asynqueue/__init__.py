# AsynQueue:
# Asynchronous task queueing based on the Twisted framework, with task
# prioritization and a powerful worker/manager interface.
#
# Copyright (C) 2006-2007 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
Priority queueing of tasks to one or more threaded or asynchronous workers.
"""

from workers import *
from base import TaskQueue


class ThreadQueue(TaskQueue):
    """
    I am a task queue for dispatching arbitrary callables to be run by workers
    from a pool of I{N} worker threads, the number I{N} being specified as the
    sole argument of my constructor.
    """
    def __init__(self, N, **kw):
        TaskQueue.__init__(self, **kw)
        for null in xrange(N):
            worker = ThreadWorker()
            self.attachWorker(worker)
