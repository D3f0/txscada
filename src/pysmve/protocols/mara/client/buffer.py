from twisted.python.constants import Names, NamedConstant
from ...constants import frame, quantity
from Queue import Queue


__all__ = ['MaraFrameReassembler', ]


class MaraFrameReassembler(object):
    '''
    Buffer for packages that performs basic validation (size, sof).
    Currently it does not perform any look behind validation. So if there's a parasite
    SOF byte it makes a whole frame to be dropped.

    For reading files,
    b = MaraFrameReassembler()
    b += open('data').read()
    print b.has_package()

    '''

    _state = None

    class states(Names):
        WAIT_SOF = NamedConstant()
        WAIT_QTY = NamedConstant()
        CONSUME_QTY = NamedConstant()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        assert value in self.states.iterconstants(), "Invalid state"
        # print(self.state, '->', value)
        self._state = value

    def __init__(self):
        self.reset()
        self._queue = Queue()

    def reset(self):
        self._buffer = ''
        self.state = self.states.WAIT_SOF
        self.remaining = 0

    def receive(self, data):
        '''This method should be called when a chunk of data comes from the wire
        It's more convenient to use += operator.
        '''
        for c in data:
            val = ord(c)
            if self.state == self.states.WAIT_SOF:
                if val == frame.SOF.value:
                    self._buffer += c
                    self.state = self.states.WAIT_QTY

            elif self.state == self.states.WAIT_QTY:
                if quantity.MIN.value <= val <= quantity.MAX.value:
                    self._buffer += c
                    self.remaining = val - len(self)
                    self.state = self.states.CONSUME_QTY
                else:
                    self.reset()
            elif self.state == self.states.CONSUME_QTY:
                self._buffer += c
                self.remaining -= 1
                if self.remaining == 0:
                    # Package recevied!
                    self._save_buffer()
                    self.state = self.states.WAIT_SOF

    def _save_buffer(self):
        self._queue.put(self._buffer)

    def has_package(self):
        '''Returns weather the buffer has a full mara frame'''
        return not self._queue.empty()

    def get_package(self):
        '''You must check that there's a package availabe before calling this method'''
        return self._queue.get(timeout=0)

    def __iadd__(self, data):
        '''Lets you use the += opperator to add stuff to frame'''
        if isinstance(data, basestring):
            self.receive(data)
        elif isinstance(data, list):
            self.receive(''.join(map(chr, data)))
        elif isinstance(data, int):
            self.receive(chr(data))
        else:
            raise ValueError(data)
        return self

    def __len__(self):
        return len(self._buffer)
