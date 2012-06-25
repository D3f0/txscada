'''
Implementation of a Twisted Modbus Server
------------------------------------------

Example run::

    context = ModbusServerContext(d=[0,100], c=[0,100], h=[0,100], i=[0,100])
    reactor.listenTCP(502, ModbusServerFactory(context))
    reactor.run()
'''
from binascii import b2a_hex
from tornado import ioloop
from tornado import iostream
from tornado import options
import socket
import fcntl
import errno
import pickle
import sys, os
sys.path.append(os.path.abspath('../'))

from pymodbus.constants import Defaults
from pymodbus.factory import ServerDecoder
from pymodbus.datastore import ModbusServerContext
from pymodbus.device import ModbusControlBlock
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.transaction import ModbusSocketFramer
from pymodbus.interfaces import IModbusFramer
from pymodbus.mexceptions import *
from pymodbus.pdu import ModbusExceptions as merror

__all__ = [ "StartServer" ]

#---------------------------------------------------------------------------#
# Server
#---------------------------------------------------------------------------#
class ModbusServer(object):
    
    def __init__(self, request_callback, no_keep_alive=False, io_loop=None, xheaders=False):
        self.request_callback = request_callback
        self.no_keep_alive = no_keep_alive
        self.io_loop = io_loop or ioloop.IOLoop.instance()
        self.xheaders = xheaders
        self._socket = None

    def listen(self, port):
        assert not self._socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        flags = fcntl.fcntl(self._socket.fileno(), fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(self._socket.fileno(), fcntl.F_SETFD, flags)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(0)
        self._socket.bind(("", port))
        self._socket.listen(128)
        self.io_loop.add_handler(self._socket.fileno(), self._handle_events, self.io_loop.READ)

    def _handle_events(self, fd, events):
        while True:
            try:
                connection, address = self._socket.accept()
            except socket.error, e:
                if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    return
                raise
            try:
                stream = iostream.IOStream(connection, io_loop=self.io_loop)
                ModbusConnection(stream, address, self.request_callback,
                               self.no_keep_alive, self.xheaders)
            except:
                pass

class ModbusConnection(object):
    """Handles a connection to an HTTP client, executing HTTP requests.

    We parse HTTP headers and bodies, and execute the request callback
    until the HTTP conection is closed.
    """
    def __init__(self, stream, address, request_callback, no_keep_alive=False, xheaders=False):
        self.stream = stream
        self.address = address
        self.request_callback = request_callback
        self.no_keep_alive = no_keep_alive
        self.xheaders = xheaders
        self._request = None
        self._request_finished = False
        self.framer = self.request_callback.framer(decoder=self.factory.decoder)
        self.stream.read_bytes(1, self._on_data)

    def send(self, message):
        assert self._request, "Request closed"
        pdu = self.framer.buildPacket(message)
        self.stream.write(pdu)

    def finish(self):
        assert self._request, "Request closed"
        self._request_finished = True
        if not self.stream.writing():
            self._finish_request()

    def _on_data(self, data):
        '''
        Callback when we receive any data
        @param data The data sent by the client
        '''
        # if not self.factory.control.ListenOnly:
        self.framer.processIncomingPacket(data, self.execute)

#---------------------------------------------------------------------------#
# Extra Helper Functions
#---------------------------------------------------------------------------#
    def execute(self, request):
        '''
        Executes the request and returns the result
        @param request The decoded request message
        '''
        self._request = request
        try:
            response = request.execute(self.request_callback.store)
        except Exception, ex:
            response = request.doException(merror.SlaveFailure)
        #self.framer.populateResult(response)
        response.transaction_id = request.transaction_id
        response.uint_id = request.unit_id
        self.send(response)

class ModbusApplication(object):
    def __init__(self, store, framer=None, identity=None):
        ''' Overloaded initializer for the modbus factory

        If the identify structure is not passed in, the ModbusControlBlock
        uses its own empty structure.

        :param store: The ModbusServerContext datastore
        :param framer: The framer strategy to use
        :param identity: An optional identify structure

        '''
        self.decoder = ServerDecoder()
        if isinstance(framer, IModbusFramer):
            self.framer = framer
        else: self.framer = ModbusSocketFramer

        if isinstance(store, ModbusServerContext):
            self.store = store
        else: self.store = ModbusServerContext()

        self.control = ModbusControlBlock()
        if isinstance(identity, ModbusDeviceIdentification):
            self.control.Identity.update(identity)

#---------------------------------------------------------------------------# 
# Starting Factories
#---------------------------------------------------------------------------# 
def StartServer(context, identity=None):
    ''' Helper method to start the Modbus Async TCP server
    :param context: The server data context
    :param identify: The server identity to use
    '''
    framer = ModbusSocketFramer
    modbus_server = ModbusServer(ModbusApplication(store=context, framer=framer, identity=identity))
    modbus_server.listen(options.port)
    ioloop.IOLoop.instance().start()
    
#--------------------------------------------------------------------------#
# Logging
#--------------------------------------------------------------------------#
import logging
logging.basicConfig()

server_log   = logging.getLogger("pymodbus.server")
protocol_log = logging.getLogger("pymodbus.protocol")

#--------------------------------------------------------------------------#
# Helper Classes
#--------------------------------------------------------------------------#
class ConfigurationException(Exception):
    ''' Exception for configuration error '''

    def __init__(self, string):
        ''' Initializes the ConfigurationException instance

        :param string: The message to append to the exception
        '''
        Exception.__init__(self, string)
        self.string = string

    def __str__(self):
        ''' Builds a representation of the object

        :returns: A string representation of the object
        '''
        return 'Configuration Error: %s' % self.string

class Configuration:
    '''
    Class used to parse configuration file and create and modbus
    datastore.

    The format of the configuration file is actually just a
    python pickle, which is a compressed memory dump from
    the scraper.
    '''

    def __init__(self, config):
        '''
        Trys to load a configuration file, lets the file not
        found exception fall through

        :param config: The pickled datastore
        '''
        try:
            self.file = open(config, "r")
        except Exception:
            raise ConfigurationException("File not found %s" % config)

    def parse(self):
        ''' Parses the config file and creates a server context
        '''
        handle = pickle.load(self.file)
        try: # test for existance, or bomb
            dsd = handle['di']
            csd = handle['ci']
            hsd = handle['hr']
            isd = handle['ir']
        except Exception:
            raise ConfigurationException("Invalid Configuration")
        return ModbusServerContext(d=dsd, c=csd, h=hsd, i=isd)

def main():
    ''' Server launcher '''
    from optparse import OptionParser
    from pymodbus.datastore import ModbusServerContext
    
    parser = OptionParser()
    parser.add_option("-c", "--conf",
                    help="The configuration file to load",
                    dest="file")
    parser.add_option("-D", "--debug",
                    help="Turn on to enable tracing",
                    action="store_true", dest="debug", default=False)
    (opt, arg) = parser.parse_args()

    # enable debugging information
    if opt.debug:
        try:
            server_log.setLevel(logging.DEBUG)
            protocol_log.setLevel(logging.DEBUG)
        except Exception, e:
            print "Logging is not supported on this system"

    # parse configuration file and run
    try:
        conf = Configuration(opt.file)
        StartServer(context=conf.parse())
    except ConfigurationException, err:
        print err
        parser.print_help()

if __name__ == '__main__':
    main()