# ecoding: utf8
# -----------------------------------------------------------------
# Gneric class attribute based StateMachine machine
# Designed to replace ad hoc definition of 
# -----------------------------------------------------------------

from constants import *
import re
from collections import OrderedDict, namedtuple
from utils.checksum import check_cs_bigendian
from utils.checksum import make_cs_bigendian

class Condition(object):
    def __init__(self, arg):
        self.arg = arg
    
    def check(self, value):
        """docstring for %s"""
        return value == self.arg
    
    def __repr__(self):
        return "Condition"



class Range(Condition):
    def __init__(self, range_min, range_max):
        """Range"""
        assert range_min < range_max, "range_min must be less than range_max"
        self.range_min, self.range_max = range_min, range_max
    
    def check(self, x):
        """Evaluates if condition is met"""
        return self.range_min < x < self.range_max
    
    def __repr__(self):
        return "Range from %s to %s" % (self.range_min, self.range_max)

class Set(Condition):
    def __init__(self, *values):
        self.values_set = set(values)
    
    def check(self, value):
        """docstring for %s"""
        return value in self.values_set
    
    def __repr__(self):
        return "Set (%s)" % self.values_set
    
class Any(Condition):
    def check(self, other):
        return True
    
    def __repr__(self):
        return "Any"

ANY = Any(None)

Transition = namedtuple('Transition', 'input_condition extra_condition to_state action initial accepts')

class StateMachine(object):
    '''State machine'''
    START_STATE = None
    TRANSITIONS = [
        # { 'from: STATE, 'with': SYMBOL, 'and': EXTRA_CONDITION, 'to': NEXT_STATE, 'whit': TRANSITION_FUNCTION, 'action': ACTION}
    ]
    _state = None
    def __init__(self):
        """docstring for %s"""
        self._table = OrderedDict()
        self._buildTransitionTable()
        self.state = self.START_STATE 
    
    def _buildTransitionTable(self):
        """Builds transition table from TRANSITION property"""

        for n, trans in enumerate(self.TRANSITIONS):
            from_state = trans.pop('from', None)
            input_condition = trans.pop('with', None)
            # Extra condition applied on the automata, should not have side effects!
            extra_condition = trans.pop('and', None)
            # Action to be taken
            to_state = trans.pop('to', None)
            # Action to be taken
            action = trans.pop('action', None)
            
            initial = trans.pop('initial', False)
            
            # Transition accepts
            accepts = trans.pop('accepts', False)
            assert not len(trans), "Some things were not processed %s" % trans.keys()
            try:
                self.add_transition(from_state = from_state,
                                    to_state = to_state,
                                    input_condition=input_condition,
                                    extra_condition=extra_condition,
                                    initial=initial,
                                    action=action, 
                                    accepts=accepts)
            except ValueError as e:
                print "Error with transition %d %s %s" % (n, trans, e)
                raise
    
    def add_transition(self, from_state, to_state, input_condition, extra_condition = None, 
                       initial = False,
                       action = None,
                       accepts=False):
        '''
        Add a transttion to the table
        :param from_state:
        :param to_state:
        :param input_condition:
        :param extra_condition: Extra condition to be met, shoudl not have side effects
        :param initial:
        '''
        # Mandatory elements
        if from_state is None: raise ValueError("Missing 'from' state")
        if to_state is None: raise ValueError("Missing 'to' state")
        if input_condition is None: raise ValueError("Missing 'with'")
        state = self._table.setdefault(from_state, []) # List of transitions
        if isinstance(input_condition, int):
            input_condition = Condition(input_condition)
        assert isinstance(input_condition, Condition), "with has an ivalid input condition"
        transition = {'input_condition': input_condition, 'extra_condition': extra_condition, 'to_state': to_state}
        if action is not None:
            if isinstance(action, basestring):
                f = getattr(self, action, None)
                if f is None: raise ValueError("Action '%s' has not been found or is not callable" % action)
                action = f
            
            if callable(action):
                transition['action'] = action
            else:
                raise ValueError("Can't use action %s" % action)
        transition = Transition(input_condition,  extra_condition,  to_state,  action, initial,  accepts)
        state.append(transition)
    
    @property
    def empty(self):
        return len(self) == 0
        
    def __len__(self):
        """Transition table length"""
        return len(self._table)
    
    def feed(self, char):
        '''Consumes one character
        :returns True if reached an state'''
        if isinstance(char, basestring):
            raise ValueError("La entrada debe de caracter debe ser de longitud 1: %s %s" % (char, len(char)))
        transitions = self._table[self.state]
        #print char, transitions 
        for n, trans in enumerate(transitions):
            #if self.state == 'wait_com':
            #    import ipdb; ipdb.set_trace()
            if trans.input_condition.check(char): # Match
                #if callable(trans.extra_condition):
                if trans.extra_condition is not None:
                    import ipdb; ipdb.set_trace()
                    if not trans.extra_condition(self, char):
                        continue
                if callable(trans.action):
                    trans.action(char)
                print "Transition #", n
                self.state = trans.to_state
                return trans.accepts
                
    @property
    def states(self):
        return self._table.keys()
    
    def feed_hex(self, data):
        """mes a hex string in human readable format"""
        for char in re.split('[\s:]', data):
            self.feed(int(char, 16))
    
    @property
    def state(self):
        ''' StateMachine current state'''
        return self._state
    
    @state.setter
    def state(self, value):
        #assert value in self.states
        print "Channging to ", value
        
        #if self._state is not None and self._state != self.START_STATE and value == self.START_STATE:
        #    raise Exception()
        self._state = value
    
    
class MaraPacketStateMachine(StateMachine):
    START_STATE = 'start'
    TRANSITIONS = (
        #SOF
        {'from': 'start', 'with': SOF, 'to': 'wait_qty', 'initial': True},
        {'from': 'start', 'with': ANY, 'to': 'start', }, # Loop until SOF appears
        #QTY
        {'from': 'wait_qty', 'with': Range(4, 0xFE), 'to': 'wait_src', 'action': 'store_qty' }, # Valid QTY
        {'from': 'wait_qty', 'with': ANY, 'to': 'start', 'action': 'reset' }, # Back to start
        #SRC
        {'from': 'wait_src', 'with': Range(0, 31), 'to': 'wait_dst', 'action': 'store' },
        {'from': 'wait_src', 'with': ANY, 'to': 'start', 'action': 'reset' },
        #DST
        {'from': 'wait_dst', 'with': Range(0, 31), 'to': 'wait_seq', 'action': 'store' },
        {'from': 'wait_dst', 'with': ANY, 'to': 'start', 'action': 'reset' },
        # SEQ
        {'from': 'wait_seq', 'with': Set(0, 0x80), 'to': 'wait_com', 'action': 'store' },
        {'from': 'wait_seq', 'with': ANY, 'to': 'start', 'action': 'reset' },
        # COMMAND
        {'from': 'wait_com', 'with': Range(0, 0x10), 'to': 'wait_arg', 'action': 'store' ,
         'and': lambda o: o.qty > 0 },
        {'from': 'wait_com', 'with': Range(0, 0x10), 'to': 'wait_bch', 'action': 'store' , },
        {'from': 'wait_com', 'with': ANY, 'to': 'start', 'action': 'reset' },
        # ARGS
        {'from': 'wait_arg', 'with': ANY, 'to': 'wait_arg', 'action': 'store_arg',
         'and': lambda o: o.qty > 0},
        {'from': 'wait_arg', 'with': ANY, 'to': 'wait_bch', 'action': 'store_arg',
         'and': lambda o: o.qty == 0}, # Run out of arguments
        # BCH           
        {'from': 'wait_bch', 'with': ANY, 'to': 'wait_bcl', 'action': 'store'},
        # BCL
        {'from': 'wait_bcl', 'with': ANY, 'to': 'start', 'and': 'checksum_ok', 'accepts': True, 'action': 'store'},
        {'from': 'wait_bcl', 'with': ANY, 'to': 'start', 'action': 'reset',},
    )
    
    def __init__(self):
        super(MaraPacketStateMachine, self).__init__()
        self.reset(None)
        
    def store_qty(self, data):
        self.store(data)
        self.qty = data - 8 # Takes away
    
    def store(self, data):
        self.buffer.append(data)
        
    def reset(self, data):
        self.buffer = []
        
    def store_arg(self, data):
        self.store(data)
        
    def checksum_ok(self, data):
        return check_cs_bigendian(self.buffer)
        
    def accept_package(self, data):
        pass

        
        
if __name__ == '__main__':
    def makepkg():
        datos = [
                 SOF,   # Start of Frame 
                 0,     # Quantity
                 1,     # Origen
                 2,     # Destino
                 0,     # Secuencia (0 o 0x80) en mara 1.0
                 0,     # Comando 0 (Peticion de estados y eventos)
                 3,     # Cantidad de DI (Digital Input)        autom.logger.info('QTY OK, %d %s' % (entrada, type(entrada)))
                 0x0C,  # PORTA
                 0xfe,  # PORTB
                 0xac,  # PORTC
                 2,     # Cantidad de AI (Analog Input)
                 0x03,  # AI0H  
                 0xaa,  # AI0L
                 0x03,  # AI1H
                 0xaf,  # AI1L
                 0,     # Cantidad de evntos (por ahora sin eventos, poruqe son de 7 bytes
             ]
        datos[1] = len(datos) + 2 # Preagregamos el checksum
        datos += make_cs_bigendian(datos) # Concatenamos el checksum
        return datos
    
    automata = MaraPacketStateMachine()
    for c in makepkg():
        if automata.feed(c):
            print automata.buffer
            
    #automata.feed_hex('AE AE DA DE 02 B2')
    
    #print automata._table
    #print automata.state
    
    