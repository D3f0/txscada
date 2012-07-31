# encoding: utf-8
from construct import *

TCD = BitStruct('TCD',
                       Enum(BitField("evtype", 2),
                            DIGITAL=0,
                            ENERGY=1,
                        ),
                       BitField("q", 2),
                       BitField("addr485", 4),
)


BPE = BitStruct('BPE',
                       BitField("bit", 4),
                       BitField("port", 3),
                       BitField("status", 1),
)

IdleCan = BitStruct('idlecan',
                  BitField('idle', 5),
                  BitField('channel', 3) 
)

SubSec = Struct('seconds', 
              UBInt8('cseg'),
              UBInt8('dmseg'),
)

Value = BitStruct('val', 
                  BitField('q', length=2, ),
                  BitField('value', length=14,)
)

Event = Struct("Event",
                       Embed(TCD),
                       Switch("evtype", lambda ctx: ctx.evtype,  
                              {
                               "DIGITAL": Embed(BPE),
                               "ENERGY":  Embed(IdleCan),
                               }
                       ),
                       #Embed(BPE),
                       
                       UBInt8('year'),
                       UBInt8('month'),
                       UBInt8('day'),
                       UBInt8('hour'),
                       UBInt8('minute'),
                       UBInt8('seconds'),
                       
                       Switch("evtype", lambda ctx: ctx.evtype, {
                            "DIGITAL": Embed(SubSec),
                            "ENERGY":  Embed(Value),
                       }),
)

#===============================================================================
# Payload del comando 10 - Encuesta de energías al COMaster
#===============================================================================
Payload_10 = Struct("Payload_10",
                           UBInt8('canvarsys'),
                           Array(lambda ctx: ctx.canvarsys / 2, ULInt16('varsys')),
                           UBInt8('candis'),
                           Array(lambda ctx: ctx.candis / 2, ULInt16('dis')),
                           UBInt8('canais'),
                           Array(lambda ctx: ctx.canais / 2, ULInt16('ais')),
                           UBInt8('canevs'),
                           Array(lambda ctx: ctx.canevs / 10, Event),
)

MaraFrame = Struct('Mara', 
            Byte('sof'),
            Byte('length'),
            Byte('dest'),
            Byte('source'),
            Byte('sequence'),
            Byte('command'),
            Range(0, 1, Payload_10),
            #Array(lambda ctx: ctx.length - 8, UBInt8('data')),
            #OptionalGreedyRange(Payload_01),
            UBInt16('bcc')
)

def ints2buffer(hexstr):
    '''
    '''
    #parts = [chr(int(c, 16)) for c in re.split('[:\s]', hexstr)]
    parts = [ chr(an_int) for an_int in hexstr ]
    return ''.join(parts)

def hexstr2buffer(a_str):        
    '''
    "FE  01" => '\xFE\x01'    
    '''
    import re
    a_list = [ chr(int(bytestr, 16)) for bytestr in  re.split('[:\s]', a_str) if len(bytestr) ]
    return ''.join(a_list)

def any2buffer(data):
    if isinstance(data, list):
        return ints2buffer(data)
    elif isinstance(data, basestring):
        return hexstr2buffer(data)
    raise Exception("%s can't be converted to string buffer")

upperhexstr = lambda buff: ' '.join([ ("%.2x" % ord(c)).upper() for c in buff])

if __name__ == '__main__':
    import sys
    int2str = lambda l: ''.join(map(chr, l))
    #int2strgen = lambda *l: (chr(i) for i in l)
    result = MaraFrame.parse(any2buffer('FE    08    01    40    80    10    80    A7'))
    print result
    r = TCD.build(Container(evtype="ENERGY", q=1, addr485=1))
    print r
    #result.data = range(1, 10)
    print "Construyendo un evento digital de puerto "
    pkg = Event.build(Container(evtype="DIGITAL", q=0, addr485=31,
                                        bit=0, port=3, status=0, year=12, month=1, day=1, hour=12, minute=24,
                                        seconds=10, cseg=0, dmseg=10))
    
    print "Evento digital",  upperhexstr(pkg)
    sys.exit()
    pkg = MaraFrame.build(Container(sof=0xFE, length=0, source=1, dest=2, sequence=0x80, command=0x10, 
                                    #Payload_10 = Container(),
                                    Payload_10=Container(canvarsys=3, varsys=[0x2323], 
                                                         canais=3, ais=[0x1212],
                                                         candis=3, dis=[0x2233], canevs=0),
                                    bcc=0))
    print "Pkg", [ "%.2x" % ord(c) for c in pkg ]
    #MaraFrame.build()
    from IPython import embed; embed()
    