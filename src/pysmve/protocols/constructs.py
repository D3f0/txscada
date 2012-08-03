# encoding: utf-8
#===============================================================================
# Mara Protocol Structures
#===============================================================================
from construct import *
from utils.checksum import make_cs_bigendian
from construct.macros import ULInt8

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

TimerTicks = Struct('ticks', 
    #UBInt8('cseg'),
    #UBInt8('dmseg'),
    ULInt16('ticks')
)

Value = BitStruct('val', 
    BitField('q', length=2, ),
    BitField('value', length=14,)
)

Event = Struct("event",
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
    UBInt8('second'),
    
    Switch("evtype", lambda ctx: ctx.evtype, {
         "DIGITAL": Embed(TimerTicks),
         "ENERGY":  Embed(Value),
    }),
)

#===============================================================================
# Payload del comando 10 - Encuesta de energías al COMaster
#===============================================================================
Payload_10 = Struct("payload_10",
    ULInt8('canvarsys'),
    Array(lambda ctx: ctx.canvarsys / 2, ULInt16('varsys')),
    ULInt8('candis'),
    Array(lambda ctx: ctx.candis / 2, ULInt16('dis')),
    ULInt8('canais'),
    Array(lambda ctx: ctx.canais / 2, ULInt16('ais')),
    ULInt8('canevs'),
    Array(lambda ctx: ctx.canevs / 10, Event),
)
#===============================================================================
# Paquete Mara 14
#===============================================================================
MaraFrame = Struct('Mara', 
            ULInt8('sof'),
            ULInt8('length'),
            ULInt8('dest'),
            ULInt8('source'),
            ULInt8('sequence'),
            ULInt8('command'),
            Optional(Payload_10),
            ULInt16('bcc')
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
    a_str = a_str.strip().replace('\n', ' ')
    a_list = [ chr(int(bytestr, 16)) for bytestr in  re.split('[:\s]', a_str) if len(bytestr) ]
    return ''.join(a_list)

def any2buffer(data):
    if isinstance(data, list):
        return ints2buffer(data)
    elif isinstance(data, basestring):
        return hexstr2buffer(data)
    raise Exception("%s can't be converted to string buffer")

# Buffer -> Upper Human Readable Hex String
upperhexstr = lambda buff: ' '.join([ ("%.2x" % ord(c)).upper() for c in buff])

def dtime2dict(dtime = None):
    '''
    Converts a datetime.datetime instance into
    a dictionary suitable for ENERGY event
    timestamp
    '''
    import datetime
    if not dtime:
        dtime = datetime.datetime.now()
    d = {}
    d['year']   = dtime.year % 100 
    d['month']  = dtime.month
    d['day']    = dtime.day
    d['hour']   = dtime.hour
    d['minute'] = dtime.minute
    d['second'] = dtime.second
    # Ticks de cristal que va de 0 a 32K-1 en un segundo
    d['ticks'] = dtime.microsecond * (float(2<<14)-1) / 1000000
    return d    


def build_frame(obj, subcon=MaraFrame):
    '''Generates a mara frame, with checksum and qty'''
    stream = subcon.build(obj)
    data= "".join([
                    stream[0],
                    UBInt8('qty').build(len(stream)),
                    stream[2:-2],
                    ])
    cs = make_cs_bigendian(data)
    cs_str = Array(2, Byte('cs')).build(cs)
    return "".join((data, cs_str))

def parse_frame(buff, as_hex_string=False):
    if as_hex_string:
        buff = hexstr2buffer(buff)
    data = MaraFrame.parse(buff)
    return data

def format_frame(buff, as_hex_string=False):
    d = parse_frame(buff, as_hex_string)
    print "SOF:", d.sof
    print "SEQ:", d.length
    print "DST:", d.dest
    print "SRC:", d.source
    print "SEQ:", d.sequence
    print "CMD:", d.command
    # Payload
    if d.payload_10:
        p = d.payload_10
        print "%12s" % "CANVARSYS:", p.canvarsys, "%d valores de word de 16" % (p.canvarsys/2)
        print "%12s" % "VARSYS:",    p.varsys 
        print "%12s" % "CANDIS:",    p.candis, "%d valores de word de 16" % (p.candis/2) 
        print "%12s" % "DIS:", p.dis
        print "%12s" % "CANAIS:", p.candis, "%d valores de word de 16" % (p.canais/2)
        print "%12s" % "DIS:", p.ais
        # Eventos
    print "BCC:", d.bcc
        

def test():
    '''Testing de tramas y subtramas'''

    int2str = lambda l: ''.join(map(chr, l))
    #int2strgen = lambda *l: (chr(i) for i in l)
    result = MaraFrame.parse(any2buffer('FE    08    01    40    80    10    80    A7'))
    print result
    r = TCD.build(Container(evtype="ENERGY", q=1, addr485=1))
    print r
    #result.data = range(1, 10)
    event_data = Container(evtype="DIGITAL", 
                            q=0, addr485=5, 
                            bit=0, port=3, status=0, 
                            year=12, month=1, day=1, 
                            hour=12, minute=24,
                            second=10, 
                            ticks=4212)
    
    print "Construyendo un evento digital de puerto con puerto 3, bit 0, estado 0" #event_data
    pkg = Event.build(event_data)
    print upperhexstr(pkg)
    print "Evento de energía"
    energy_data = Container(evtype="ENERGY", q=0, addr485=4,
                            idle=0, channel=0, 
                            value=0x032F, 
                            **dtime2dict())
    pkg = Event.build(energy_data)
    print upperhexstr(pkg)
    
    print "Construyendo payload del comando 10"
    payload_10_data = Container(canvarsys=5, varsys=[0x1234, 0xfeda], candis=3, dis=[0x4567],  canais=0,ais=[], canevs=31, event=[event_data, event_data, energy_data])
    
    pkg = Payload_10.build(payload_10_data)
    print upperhexstr(pkg)
    frame_data = Container(sof=0xFE, length=0, source=1, dest=2, sequence=0x80, command=0x10, 
                                    payload_10=payload_10_data,
                                    bcc=0)
    pkg = MaraFrame.build(frame_data)
    
    print "Trama Mara c/QTY=0 y sin CS: ",  upperhexstr(pkg)
    print "Trama completa:", upperhexstr(build_frame(frame_data))

if __name__ == '__main__':
    #===========================================================================
    # Debug with ipython --pdb -c "%run constructs.py"
    #===========================================================================
    
    import sys
    
    # test()
    
    print "-"*80
    print "Trama 1"
    print "-"*80
    trama_1 = """
    FE 44 40 01 4A 10 19 00 00 90 1D 01 00 00 00 00 00 80 80 00 00 80 80 00 00 80 80 00
    00 80 80 0F 00 00 43 00 00 00 00 04 00 04 00 04 00 04 13 48 05 51 00 51 00 51 00 51
    00 51 00 51 00 51 00 51 00 01 E1 29
    """
    # Primera trama
    format_frame(trama_1, as_hex_string=True)
    
    
    print "-"*80
    print "Trama 2"
    print "-"*80
    trama_2 = """
    FE 44 40 01 4C 10 19 00 00 85 1D 01 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 01 0F 
    00 00 43 00 00 00 00 04 00 04 00 04 00 04 13 4C 05 51 00 51 00 51 00 51 00 51 00 51 00 51 00 51 
    00 01 DD 30
    """
    # Segunda trama
    format_frame(trama_2, as_hex_string=True)

    print "-"*80
    print "Trama 3"
    print "-"*80
    trama_3 = """
    FE F8 40 01 4D 10 19 00 00 8D 1D 01 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 01 0F
    00 00 43 00 00 00 00 04 00 04 00 04 00 04 13 81 09 51 00 51 00 51 00 51 00 51 00 51 00 51 00 51
    00 B5 01 93 0C 01 01 01 08 22 00 14 01 E3 0C 01 01 01 08 22 00 14 01 05 0C 01 01 01 08 22 00 14 
    01 92 0C 01 01 01 08 22 00 18 01 E2 0C 01 01 01 08 22 00 18 01 04 0C 01 01 01 08 22 00 18 01 F1 
    0C 01 01 01 08 22 00 1C 01 93 0C 01 01 01 08 22 00 1C 01 F3 0C 01 01 01 08 22 00 1C 01 05 0C 01 
    01 01 08 22 00 1C 01 F2 0C 01 01 01 08 22 00 20 01 04 0C 01 01 01 08 22 00 20 01 F0 0C 01 01 01 
    08 22 00 24 01 92 0C 01 01 01 08 22 00 24 01 15 0C 01 01 01 08 22 00 60 01 14 0C 01 01 01 08 22 
    00 7C 01 F3 0C 01 01 01 08 23 00 00 01 15 0C 01 01 01 08 23 00 00 3C 91
    """
    # Tercer trama
    format_frame(trama_3, as_hex_string=True)
    
    
    