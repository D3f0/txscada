import sys
import zmq

port = "5560"
# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
print "Collecting updates from server..."
socket.connect ("tcp://localhost:%s" % port)
topicfilter = "ALFA"
#socket.setsockopt(zmq.SUBSCRIBE, 'ALFA')
#socket.setsockopt(zmq.SUBSCRIBE, 'BETA')
socket.setsockopt(zmq.SUBSCRIBE, '')
for update_nbr in range(10):
    string = socket.recv()
    topic, messagedata = string.split()
    print topic, messagedata
