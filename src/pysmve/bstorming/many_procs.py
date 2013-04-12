"""
Process in multiprocessing library
"""

import os
import sys
from time import sleep
import signal
from multiprocessing import Process

def func(id, interval=0.5):
    while True:
        print "%s -> %s" % (id, os.getpid())
        sleep(interval)

def finish(p):
    try:
        p.terminate()
    except Exception, e:
        print e

def main():
    procs = []
    for letter in ('A', 'B', 'C'):
        p = Process(target=func, args=(letter, ))
        p.start()
        procs.append(p)

    try:
        map(lambda p: p.join(), procs)
    except KeyboardInterrupt, e:
        map(finish, procs)


if __name__ == '__main__':
    sys.exit(main())