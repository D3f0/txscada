# encoding: utf-8

from django.core.management.base import NoArgsCommand, CommandError
from apps.mara.models import Profile
from twisted.internet import reactor
from optparse import make_option
from protocols.mara import client
# MaraClientProtocolFactory,
# MaraClientDBUpdater,
# MaraClientPackageRedisPublisher
from django.conf import settings
from multiprocessing import Process
import logging


def dbsaver(frame_queue_address):
    '''
    Pops frames from a ZMQ queue (PUB/SUB) and save them to
    database. It executes blocking django code that may hurt twisted
    asynchronous nature

    [twisted poll] ---> [ queue device] ---> [dbsaver]
    '''
    import redis
    connection = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT,
                                   password=settings.REDIS_PASSWORD,)
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(frame_queue_address)

    while True:
        data = sock.get_data()
        if data['msg_type'] == 'FRAME':
            comaster = comasters[data['ip_address']]
            comaster.process_frame(data['frame'])


class Command(NoArgsCommand):
    '''
    Poll for data
    '''
    option_list = NoArgsCommand.option_list + (
        make_option('-p', '--profile', default=None),
        make_option('-r', '--reconnect', default=False,
                    action='store_true'),
        make_option('-n', '--no-defer-db', default=True,
                    action='store_false', dest='defer_db_save'
                    )
    )

    def get_profile(self, name):
        '''Get the profile'''
        if name is None:
            return Profile.objects.get(default=True)
        else:
            try:
                return Profile.objects.get(name__iexact=name)
            except Profile.DoesNotExist:
                raise CommandError("Profile named %s does not exist" % name)

    def handle_noargs(self, **options):
        self.logger = logging.getLogger('commands')

        profile = self.get_profile(options.get('profile'))

        # COnfigure Protocol
        client.MaraClientProtocolFactory.protocol = client.MaraClientDBUpdater
        # Redis class setup
        #MaraClientProtocolFactory.protocol.redis_host = settings.REDIS_HOST
        #MaraClientProtocolFactory.protocol.redis_port = settings.REDIS_PORT
        #MaraClientProtocolFactory.protocol.redis_password = settings.REDIS_PASSWORD
        reconnect = options.get('reconnect')
        for comaster in profile.comasters.filter(enabled=True):
            self.logger.debug("Conectando con %s" % comaster)
            client_fatory = client.MaraClientProtocolFactory(comaster=comaster,
                                                             reconnect=reconnect
                                                             )
            reactor.connectTCP(host=comaster.ip_address,
                               port=comaster.port,
                               factory=client_fatory,
                               timeout=comaster.poll_interval,
                               )
            # Una vez que está conectado todo, debemos funcionar...
        reactor.run()
