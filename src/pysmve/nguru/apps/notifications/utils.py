import os
import serial
from logging import getLogger
from time import sleep
from datetime import datetime


logger = getLogger(__name__)

TIME_FORMAT = '%Y%m%d%H%M%S'
PORT = os.environ.get('PORT', '/dev/ttyACM0')
BAUDRATE = int(os.environ.get('BAUDRATE', 230400))
TIMEOUT = int(os.environ.get('TIMEOUT', 5))


OUTGOING_QUEUE = '/var/spool/sms/outgoing'


class Modem(object):
    def send_sms(self, to, message, id=None):
        """
        @param to: Destination number
        @param message: Text message, this could be reduced to 160 chars
        @param id: some identification of the source of the message, may be null
        @returns This function does not return anything
        """
        raise NotImplementedError("You must use a subclass of %s" % type(self))


class RealModem(Modem):

    def __init__(
            self,
            port='/dev/ttyACM0',
            baudrate=BAUDRATE,
            timeout=TIMEOUT,
            rtscts=True):

        self.modem = serial.Serial(
            port=port,
            baudrate=baudrate,
            rtscts=rtscts,
            timeout=timeout
        )

    def send_sms(self, to, message, id=None):
        self.modem.write('AT+CMGF=1\r')
        resp = self.modem.read(100)  # Wait
        self.modem.write(map(ord, 'AT+CMGS="%s"\r' % to))
        resp = self.modem.read(100)  # Wait
        self.modem.write(map(ord, message.encode('ascii', 'replace')+chr(26)))
        resp = self.modem.read(100)
        return 'OK' in resp.strip()

    def __del__(self):
        self.modem.close()


class NullModem(Modem):
    def send_sms(self, to, message, id=None):
        logger.info("Null message to %s: %s", to, message)
        sleep(.5)
        return True


class SMSServerToolsModem(Modem):
    """
    Modem with file backend provieded by smsservertools
    Files tipically are stored in /var/spool/sms/outgoing
    and end up in /var/spool/sms/sent or /var/spool/sms/failed depending on the result.
    A good debugging technique is to run tail -f /var/log/sms/
    """
    def __init__(self, outoging_queue=OUTGOING_QUEUE, ):
        if not os.path.isdir(outoging_queue):
            raise AssertionError("%s is not a valid directory" % outoging_queue)
        self.outoging_queue = outoging_queue

    def send_sms(self, to, message, id=None):
        if id is None:
            id = 'NA'
        current_time_formated = self.get_current_time_formated()
        filename = '%s-%s-%s' % (current_time_formated, to, id)
        destination = os.path.join(self.outoging_queue, filename)

        assert not os.path.exists(destination), "%s exists" % destination

        with open(destination, 'w') as fp:
            fp.write(message)

    @staticmethod
    def get_current_time_formated():
        '''
        For testability reasons it's better not to burry a builtin call inside
        a method
        '''
        return datetime.now().strftime(TIME_FORMAT)


def get_available_modem():
    """Protected variations"""
    if not os.path.exists(PORT):
        logger.info("Getting null modem")
        return NullModem()
    else:
        logger.info("Getting real modem")
        return RealModem()
