from twisted.python.constants import Values, ValueConstant
__all__ = ['frame', 'sequence', 'commands', 'quantity']


class frame(Values):
    SOF = ValueConstant(0xFE)  # Start of frame (the first byte of a frame)


class sequence(Values):
    MIN = ValueConstant(0x20)
    MAX = ValueConstant(0x7F)

# ==============================================================================
# Commands
# ==============================================================================


class commands(Values):
    POLL = ValueConstant(0x10)
    PEH = ValueConstant(0x12)

# [SOF | QTY | SRC | DST | SEQ | COM | BCC1 | BCC2 ]
# [ 0  |  1  |  2  |  3  |  4  |  5  |  6   |  7   ]


class quantity(Values):
    MIN = ValueConstant(0x08)
    MAX = ValueConstant(0xFF)

# ==============================================================================
# Polling
# ==============================================================================
DEFAULT_POLL_INTERVAL = 5.0
DEFAULT_TIMEOUT = 4.9

# ==============================================================================
# Default ports and ad
# ==============================================================================

DEFAULT_COMASTER_PORT = 9761
DEFAULT_COMASTER_ADDR = '192.168.1.97'

# ==============================================================================
# Dataloger constants
# ==============================================================================
INPUT = 'i'
OUTPUT = 'o'
