# encoding: utf-8

from django.core.management.base import NoArgsCommand, CommandError
from mara.models import Profile
from twisted.internet import reactor
from optparse import make_option
from protocols.mara.client import MaraClientProtocolFactory, MaraClientDBUpdater


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

        profile = self.get_profile(options.get('profile'))

        Profile.objects.get()

        MaraClientProtocolFactory.protocol = MaraClientDBUpdater

        for comaster in profile.comasters.filter(enabled=True):
            print "Conectando con %s" % comaster
            reactor.connectTCP(comaster.ip_address,
                               comaster.port,
                               MaraClientProtocolFactory(
                               comaster,
                               reconnect=options.get('reconnect')
                               ),
                               timeout=comaster.poll_interval,
                               )
            # Una vez que está conectado todo, debemos funcionar...
        reactor.run()  # @UndefinedVariable
