import sys, os

from zope.interface import implements

from twisted.python.failure import Failure
from twisted.python.log import err
from twisted.internet.error import ConnectionDone
from twisted.internet.defer import Deferred, succeed, setDebugging
from twisted.internet.interfaces import IStreamClientEndpoint
from twisted.internet.protocol import Factory, Protocol

from twisted.conch.ssh.common import NS
from twisted.conch.ssh.channel import SSHChannel
from twisted.conch.ssh.transport import SSHClientTransport
from twisted.conch.ssh.connection import SSHConnection
from twisted.conch.client.default import SSHUserAuthClient
from twisted.conch.client.options import ConchOptions

# setDebugging(True)


class _CommandTransport(SSHClientTransport):
    _secured = False

    def verifyHostKey(self, hostKey, fingerprint):
        return succeed(True)


    def connectionSecure(self):
        self._secured = True
        command = _CommandConnection(
            self.factory.command,
            self.factory.commandProtocolFactory,
            self.factory.commandConnected)
        userauth = SSHUserAuthClient(
            os.environ['USER'], ConchOptions(), command)
        self.requestService(userauth)


    def connectionLost(self, reason):
        if not self._secured:
            self.factory.commandConnected.errback(reason)



class _CommandConnection(SSHConnection):
    def __init__(self, command, protocolFactory, commandConnected):
        SSHConnection.__init__(self)
        self._command = command
        self._protocolFactory = protocolFactory
        self._commandConnected = commandConnected


    def serviceStarted(self):
        channel = _CommandChannel(
            self._command, self._protocolFactory, self._commandConnected)
        self.openChannel(channel)



class _CommandChannel(SSHChannel):
    name = 'session'

    def __init__(self, command, protocolFactory, commandConnected):
        SSHChannel.__init__(self)
        self._command = command
        self._protocolFactory = protocolFactory
        self._commandConnected = commandConnected


    def openFailed(self, reason):
        self._commandConnected.errback(reason)


    def channelOpen(self, ignored):
        self.conn.sendRequest(self, 'exec', NS(self._command))
        self._protocol = self._protocolFactory.buildProtocol(None)
        self._protocol.makeConnection(self)


    def dataReceived(self, bytes):
        self._protocol.dataReceived(bytes)


    def closed(self):
        self._protocol.connectionLost(
            Failure(ConnectionDone("ssh channel closed")))



class SSHCommandClientEndpoint(object):
    implements(IStreamClientEndpoint)

    def __init__(self, command, sshServer):
        self._command = command
        self._sshServer = sshServer


    def connect(self, protocolFactory):
        factory = Factory()
        factory.protocol = _CommandTransport
        factory.command = self._command
        factory.commandProtocolFactory = protocolFactory
        factory.commandConnected = Deferred()

        d = self._sshServer.connect(factory)
        d.addErrback(factory.commandConnected.errback)

        return factory.commandConnected



class StdoutEcho(Protocol):
    def dataReceived(self, bytes):
        sys.stdout.write(bytes)
        sys.stdout.flush()


    def connectionLost(self, reason):
        self.factory.finished.callback(None)



def copyToStdout(endpoint):
    echoFactory = Factory()
    echoFactory.protocol = StdoutEcho
    echoFactory.finished = Deferred()
    d = endpoint.connect(echoFactory)
    d.addErrback(echoFactory.finished.errback)
    return echoFactory.finished



def main():
    from twisted.python.log import startLogging
    from twisted.internet import reactor
    from twisted.internet.endpoints import TCP4ClientEndpoint

    # startLogging(sys.stdout)

    sshServer = TCP4ClientEndpoint(reactor, "localhost", 22)
    commandEndpoint = SSHCommandClientEndpoint("/bin/ls", sshServer)

    d = copyToStdout(commandEndpoint)
    d.addErrback(err, "ssh command / copy to stdout failed")
    d.addCallback(lambda ignored: reactor.stop())
    reactor.run()


main()
