#!/usr/bin/env python2
from copy import copy
from .bitfield import iterbits


def expand(values, lengths, input_width=8):
    if not values:
        return
    #assert sum(lengths) <= input_width * len(values)
    while lengths and values:
        if lengths[:8] == [1, 1, 1, 1, 1, 1, 1, 1]:
            lengths = lengths[8:]
            for v in iterbits([values.pop(0)], 8):
                yield v
        elif lengths[0] == 8:
            yield values.pop(0)
            lengths.pop(0)


def worditer(values, widths, input_width=16):

    remain_widths = copy(widths)

    while remain_widths:
        try:
            cur_width = remain_widths.pop(0)
            if cur_width == 16:
                yield values.pop(0)
            elif cur_width == 8:
                value = values.pop(0)
                yield value & 0x00FF
                assert remain_widths.pop(
                    0) == 8, "Invalid 2-byte word alignment"
                yield (value & 0xFF00) >> 8
            else:
                raise AssertionError("Invalid length: %d" % cur_width)
        except IndexError:
            return


def main():
    values = [0xaabb, 0xccdd, 0xddee]
    splits = [15, 8, 8, 16, 8]
    print "Separando %s en %s" % (", ".join([("%x" % v).upper() for v in values]), splits)
    for v in worditer(values, splits):
        print ("%x" % v).upper()


if __name__ == '__main__':
    main()
