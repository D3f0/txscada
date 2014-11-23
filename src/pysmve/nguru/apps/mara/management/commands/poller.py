# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand, CommandError
from apps.mara.models import Profile
from twisted.internet import reactor
from optparse import make_option
from apps.mara.utils import get_setting, import_class
from django.conf import settings
import logging

logger = logging.getLogger('commands')


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

    def get_handler_classes(self):
        '''Returns a list of handler classess based on configuration'''
        configured_handlers = get_setting('POLL_FRAME_HANDLERS', [])
        if not configured_handlers:
            logger.warn("No frame handlers. Porbably no frame will be saved on DB!!!")
        classes = []
        for handler_class_name in configured_handlers:
            handler_class = import_class(handler_class_name)
            classes.append(handler_class)
        return classes

    def handle_noargs(self, **options):

        self.options = options

        self.logger = logging.getLogger('commands')

        profile = Profile.get_by_name(self.options['profile'])
        if not profile:
            raise CommandError("Profile does not exist")

        handlers = self.get_handler_classes()
        comasters = profile.comasters.filter(enabled=True)
        if not comasters.count():
            self.logger.warn("No comaster enabled.")
            return

        for comaster in comasters:
            logger.debug("Creating ClientFactory for %s" % comaster)
            protocol_factory = comaster.get_protocol_factory()
            # Create frame handler instances based on settings

            for handler in handlers:
                instance = handler(comaster, settings=settings)
                protocol_factory.handlers.append(instance)

            protocol_factory.connectTCP(reactor=reactor)

        if self.options['run']:
            reactor.run()
