from django.core.management.base import BaseCommand
from apps.notifications.models import NotificationRequest
from logging import getLogger
from optparse import make_option
from time import sleep
from apps.notifications.utils import get_available_modem
from signal import signal, SIGINT
from datetime import datetime


logger = getLogger(__name__)


_stop = False


def on_sigint(sig, stack):
    global _stop
    _stop = True


class Command(BaseCommand):
    help = "Sends SMS notifications"
    option_list = (
        make_option(
            '-o', '--one-shot',
            help='Only run one time',
            dest='run_forever', default=True,
            action='store_false'
        ),
        make_option(
            '-i', '--interval',
            help='Interval between new events checks',
            dest='sleep_time', default=10,
            type=float
        ),

        make_option(
            '-c', '--count',
            dest='count', default=False, action='store_true',
            help="Only count"
        )

    ) + BaseCommand.option_list

    def send_messages(self, modem):
        statuses = (
            NotificationRequest.STATUS_CREATED,
            NotificationRequest.STATUS_ERROR,
        )
        qs = NotificationRequest.objects.filter(status__in=statuses)
        to_send = qs.count()

        if to_send:
            logger.info("About to send %d messages", qs.count())
            qs = qs.select_for_update()
            for n, notification in enumerate(qs):

                notification.status = NotificationRequest.STATUS_PROCESSING
                notification.last_status_change_time = datetime.now()
                notification.save()
                try:
                    result = modem.send_sms(notification.destination, notification.body)
                except Exception as e:
                    notification.status = NotificationRequest.STATUS_ERROR
                    notification.last_status_change_time = datetime.now()
                    notification.save()
                    raise e

                if result:
                    notification.status = NotificationRequest.STATUS_SUCCESS
                else:
                    notification.status = NotificationRequest.STATUS_ERROR

                notification.last_status_change_time = datetime.now()
                notification.save()

                if _stop:
                    return
            logger.info("%d processed", n)
        else:
            logger.info("No events to send, sleeping %2.2fs", self.options['sleep_time'])
        sleep(self.options['sleep_time'])

    def show_counters(self):
        qs = NotificationRequest.objects.all()
        logger.info("To send: %d", qs.filter(
            status__in=NotificationRequest.STATUS_CREATED).count()
        )
        logger.info("In process: %d", qs.filter(
            status__in=NotificationRequest.STATUS_PROCESSING).count()
        )
        logger.info("Error: %d", qs.filter(
            status__in=NotificationRequest.STATUS_ERROR).count()
        )
        logger.info("Processed: %d", qs.filter(
            status__in=NotificationRequest.STATUS_SUCCESS).count()
        )

    def handle(self, *args, **options):
        self.options = options

        modem = get_available_modem()
        logger.debug("Using modem %s", modem)
        signal(SIGINT, on_sigint)
        if self.options['count']:

            return self.show_counters()

        while self.options['run_forever'] and not _stop:
            self.send_messages(modem)

        logger.info("Exited")
