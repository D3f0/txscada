from construct import *

if __name__ == '__main__':
    ints = [0x2, 0x1, 0xff]
    buffer = ''.join([chr(x) for x in ints])
    X = BitStruct('foo', BitField('alfa', 24))
    print X.parse(buffer)