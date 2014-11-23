# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand, CommandError
from apps.mara.models import Profile
from twisted.internet import reactor
from optparse import make_option
from protocols.mara import client
import logging


class Command(NoArgsCommand):
    '''
    Poll for data
    '''
    option_list = NoArgsCommand.option_list + (
        make_option('-p', '--profile', default=None),
        make_option('-r', '--reconnect', default=False,
                    action='store_true'),
        make_option('-n', '--no-run',
                    dest='run',
                    default=True,
                    action='store_false')

    )

    def handle_noargs(self, **options):
        self.options = options

        self.logger = logging.getLogger('commands')

        profile = Profile.get_by_name(self.options['profile'])
        if not profile:
            raise CommandError("Profile does not exist")

        for comaster in profile.comasters.filter(enabled=True):
            protocol_factory = comaster.get_protocol_factory()
            protocol_factory.connectTCP(reactor=reactor)

        if self.options['run']:
            reactor.run()
