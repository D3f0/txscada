from ..buffer import MaraFrameReassembler
from protocols.constants import frame


def test_buffer():
    # Alias
    MFRS = MaraFrameReassembler.states
    b = MaraFrameReassembler()
    assert b.state == MFRS.WAIT_SOF
    assert b.remaining == 0
    assert len(b) == 0

    b += 0xFF
    assert b.state == MFRS.WAIT_SOF
    # b += SOF
    #      [SOF | QTY | SRC | DST | SEQ | COM | BCC1 | BCC2 ]
    data = [frame.SOF.value,   0,    1,    1,    1,   0x10,    0,      0]
    data[1] = len(data)

    b += data
    assert b.has_package()
    assert b.state == MFRS.WAIT_SOF
