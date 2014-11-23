import logging


class COMasterLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        ip_address = self.extra['comaster'].ip_address
        return '[%s] %s' % (ip_address, msg), kwargs
