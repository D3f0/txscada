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
        make_option('-n', '--no-run',
                    dest='run',
                    default=True,
                    action='store_false'),
        make_option('-o', '--override-ip',
                    default=None,
                    dest='override_ip',
                    type=str,
                    help="For testing purpuses it allows to override configured ip in "
                         "database. This comand can be used with\t\t"
                         "$ netcat -l -p 9761 | cat -e\t\t"
                         "or with \t\t\tmanage.py server (if available).\t\t\t"
                         "Note that in this examples the port is set to the default mara"
                         "port: 9761 (comes from Microchip examples and inital code by"
                         "Ricardo A. Lopez)."),
        make_option('-m', '--max-retry',
                    dest='maxRetries',
                    type=int,
                    default=0,
                    help="Specify an amount of retries when  connection fail.\t\t"
                         "0 makes the command to retry indefenetly. In production "
                         "this value should always be 0.")
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

        if settings.DEBUG:
            self.logger.warning("DEBUG is ON in Django settings. Will leak memory!")

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
            maxRetries = self.options['maxRetries']
            if maxRetries > 0:
                protocol_factory.maxRetries = maxRetries

            for handler in handlers:
                instance = handler(comaster, settings=settings)
                protocol_factory.handlers.append(instance)

            protocol_factory.connectTCP(reactor=reactor,
                                        override_ip=self.options['override_ip'])

        if self.options['run']:
            reactor.run()
