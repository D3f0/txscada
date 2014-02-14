from django.core.management.base import NoArgsCommand, CommandError
from apps.mara.models import Profile
from twisted.internet import reactor
from optparse import make_option
#from protocols.mara.client import MaraClientProtocolFactory, MaraClientDBUpdater
import logging
from multiprocessing import Process
import zmq
from zmq.devices import ProcessDevice
import time

import random, os


QUEUE_IN = 'ipc:///tmp/queue_in'
QUEUE_OUT = 'ipc:///tmp/queue_out'


def producer(destination_socket):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(QUEUE_IN)
    counter = 0
    while True:
        time.sleep(0.1)
        socket.send("%d" % counter)
        counter += 1
        if counter > 10:
            return

def consumer(source_socket):
    random.seed(os.getpid())
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect(QUEUE_OUT)
    while True:
        data = socket.recv()
        print "Data:", data
        time.sleep(0.5)


class Command(NoArgsCommand):
    def start_device(self):
        queuedevice = ProcessDevice(zmq.QUEUE, zmq.PULL, zmq.PUSH)
        queuedevice.bind_in(QUEUE_IN)
        queuedevice.bind_out(QUEUE_OUT)
        #queuedevice.setsockopt_in(zmq.HWM, 1)
        #queuedevice.setsockopt_out(zmq.HWM, 1)
        queuedevice.start()

    def handle_noargs(self, **options):
        print "HOLA"
        self.start_device()
        print "Device started"
        time.sleep(1)
        prod = Process(target=producer, args=(QUEUE_IN, ))
        prod.start()
        cons = Process(target=consumer, args=(QUEUE_OUT, ))
        cons.start()
        prod.join()
        cons.join()


