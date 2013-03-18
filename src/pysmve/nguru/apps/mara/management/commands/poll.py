# encoding: utf-8

from django.core.management.base import NoArgsCommand, CommandError
from mara.models import Profile
from twisted.internet import reactor
from optparse import make_option
from protocols.mara.client import MaraClientProtocolFactory, MaraClientDBUpdater
import logging

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('-p', '--profile', default=None),
        make_option('-r', '--reconnect', default=False,
                    action='store_true'),
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

        Profile.objects.get()

        MaraClientProtocolFactory.protocol = MaraClientDBUpdater

        for comaster in profile.comasters.filter(enabled=True):
            self.logger.debug("Conectando con %s" % comaster)
            client_fatory = MaraClientProtocolFactory(
                                comaster,
                                reconnect=options.get('reconnect')
                            )
            reactor.connectTCP(host=comaster.ip_address,
                               port=comaster.port,
                               factory=client_fatory,
                               timeout=comaster.poll_interval,
                               )
            # Una vez que está conectado todo, debemos funcionar...
        reactor.run()
