from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings
import zmq
import random
import json
import time


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)

        endpoint = '{0}://localhost:{1}'.format(
            settings.FORWARDER_SUB_TRANSPORT,
            settings.FORWARDER_SUB_PORT
        )
        publisher_id = random.randrange(0, 9999)
        try:
            socket.connect(endpoint)
        except zmq.error.ZMQError:
            raise CommandError("Cant connect to %s" % endpoint)

        print "Demo Data being sent to %s with id: %s" % (endpoint, publisher_id)
        try:
            while True:
                topic = random.choice(['value_update', 'full_refresh', 'event', 'echo'])
                messagedata = "server#%s" % publisher_id
                print "%s %s" % (topic, messagedata)
                socket.send(json.dumps({'id': 1, 'status': False, 'type': topic}))
                self.sleep()

        except KeyboardInterrupt:
            raise CommandError("Interrupted")

    def sleep(self):
        time.sleep(random.randrange(10, 1000)*0.0001)
