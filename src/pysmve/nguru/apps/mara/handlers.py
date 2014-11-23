from twisted.internet import reactor


class FrameHandler(object):
    def __init__(self, comaster, **options):
        raise NotImplementedError(type(self))

    def handle_frame(self, frame):
        raise NotImplementedError(type(self))


class DjangoORMMaraFrameHandler(FrameHandler):

    def __init__(self, comaster, settings=None):
        self._comaster = comaster

    def handle_frame(self, mara_frame):
        if reactor.running:
            return reactor.callInThread(self.saveInDatabase, mara_frame)
        else:
            return self.saveInDatabase(mara_frame)

    def saveInDatabase(self, mara_frame):
        self._comaster.process_frame(mara_frame)


class AMQPPublishHandler(FrameHandler):
    pass