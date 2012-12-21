# encoding: utf-8

from django.core.management.base import NoArgsCommand, CommandError
from twisted.internet import reactor
from optparse import make_option
from protocols.mara.client import MaraClientProtocolFactory, MaraClientDBUpdater


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('-p', '--profile', default='default'),
        make_option('-r', '--reconnect', default=False,
                    action='store_true'),
    )
    def handle_noargs(self, **options):
        from mara.models import Profile
        try:
            name = options.get('profile')
            profile = Profile.objects.get(name__iexact=name)
        except Profile.DoesNotExist:
            raise CommandError("Profile named %s does not exist" % name)

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
        reactor.run() #@UndefinedVariable
