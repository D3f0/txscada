import os
import serial
from logging import getLogger
from time import sleep

logger = getLogger(__name__)


PORT = os.environ.get('PORT', '/dev/ttyACM0')
BAUDRATE = int(os.environ.get('BAUDRATE', 230400))
TIMEOUT = int(os.environ.get('TIMEOUT', 5))

class Modem(object):
    def send_sms(self, to, message):
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

    def send_sms(self, to, message):
        self.modem.write('AT+CMGF=1\r')
        resp = self.modem.read(100)  # Wait
        self.modem.write('AT+CMGS="%s"\r' % to.encode('latin1', 'ignore'))
        resp = self.modem.read(100)  # Wait
        self.modem.write(str(message).encode('latin1', 'ignore')+chr(26))
        resp = self.modem.read(100)
        return 'OK' in resp.strip()

    def __del__(self):
        self.modem.close()


class NullModem(Modem):
    def send_sms(self, to, message):
        logger.info("Null message to %s: %s", to, message)
        sleep(.5)
        return True


def get_available_modem():
    """Protected variations"""
    if not os.path.exists(PORT):
        logger.info("Getting null modem")
        return NullModem()
    else:
        logger.info("Getting real modem")
        return RealModem()
