from base import MaraClientProtocol
from txredis.client import RedisClient
from twisted.internet import protocol


class MaraClientPackageRedisPublisher(MaraClientProtocol):
    '''
    Every time a package has been received, it sends it through
    Redis for processing
    '''
    # Settings
    redis_host = None
    redis_port = None
    redis_password = None
    # Connection
    redis_connection = None

    def connectionMade(self):
        self.logger.debug("Connecting to REDIS for JOB dispatching")
        self._clientCreator = protocol.ClientCreator(reactor, RedisClient)
        self.redis_connection = yield clientCreator.connectTCP(self.redis_host,
                                                               self.redis_port
                                                               )
        super(MaraClientPackageRedisPublisher, self).connectionMade()

    def saveInDatabase(self):

        yield self.redis_connection.rpush(self.redis_work_queue)