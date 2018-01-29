import zmq
import random
import json
import time

#port = "5559"
port = 4400
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect("tcp://localhost:%s" % port)
publisher_id = random.randrange(0,9999)
while True:
    topic = random.choice(['value_update', 'full_refresh', 'event'])
    messagedata = "server#%s" % publisher_id
    print "%s %s" % (topic, messagedata)
    socket.send("%s %s" % (topic, json.dumps({'id':1, 'status': False, })))
    time.sleep(random.randrange(10, 1000)*0.001)
