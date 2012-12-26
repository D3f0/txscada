# encoding: utf-8
#===============================================================================
# Mara Protocol Structures
#===============================================================================
from construct import *
from datetime import datetime
from ..utils.checksum import make_cs_bigendian
from ..utils.bitfield import bitfield
from .. import constants
from adapters import (EnergyValueAdapter,
                      MaraDateTimeAdapter,
                      SubSecondAdapter)
from adapters import PEHAdapter

#===============================================================================
# Mara protocol SubConstructs
#===============================================================================

TCD = BitStruct('TCD',
    Enum(
         BitField("evtype", 2),
            DIGITAL=0,
            ENERGY=1,
            #INVALID_2=2,
            #INVALID_3=3
    ),
    BitField("q", 2),
    BitField("addr485", 4),
)

#=========================================================================================
# Old Bit Port Status
# Deprecated since mara 1.4v11
#=========================================================================================

BPE = BitStruct('BPE',
    BitField("bit", 4),
    BitField("port", 3),
    BitField("status", 1),
)

EPB = BitStruct('BPE',
    BitField("status", 1),
    BitField("port", 3),
    BitField("bit", 4),
)


IdleCan = BitStruct('idlecan',
    BitField('idle', 5),
    BitField('channel', 3)
)

CodeCan = BitStruct('codecan',
    BitField('idle', 2),
    BitField('code', 3),
    BitField('channel', 3)
)

TimerTicks = Struct('ticks',
    #UBInt8('cseg'),
    #UBInt8('dmseg'),
    ULInt16('ticks')
)

Value = BitStruct('val',
    BitField('q', length=2,),
    BitField('value', length=14,)
)


DateTime = Struct('datetime',
    UBInt8('year'),
    UBInt8('month'),
    UBInt8('day'),
    UBInt8('hour'),
    UBInt8('minute'),
    UBInt8('second'),
)



Event = Struct("event",
    Embed(TCD),
    Switch("evdetail", lambda ctx: ctx.evtype,
           {
            "DIGITAL": Embed(EPB),
            "ENERGY":  Embed(IdleCan),
            }
    ),

    UBInt8('year'),
    UBInt8('month'),
    UBInt8('day'),
    UBInt8('hour'),
    UBInt8('minute'),

    UBInt8('second'),

    If(lambda ctx: ctx['evtype'] == "DIGITAL",
       #Embed(SubSecondAdapter(ULInt16('ticks'))),
       SubSecondAdapter(ULInt16('subsec'))
    ),

    If(lambda ctx: ctx.evtype == "ENERGY",
       EnergyValueAdapter(ULInt16('value')),
    ),


    #Switch("taildata", lambda ctx: ctx.evtype, {
    #    "DIGITAL": ULInt16('ticks'),
    #    #"ENERGY":  EnergyValueAdapter(ULInt16('copete')),
    #    "ENERGY":  ULInt16('value'),
    #}, default = Pass),
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


Payload_PEH = Struct("peh",
    ULInt8('year'),
    ULInt8('month'),
    ULInt8('day'),
    ULInt8('hour'),
    ULInt8('minute'),
    ULInt8('second'),
    # Subsecond
    ULInt8('fsegl'),
    ULInt8('fsegh'),
    # Day of week
    ULInt8('day_of_week'),
)
#===============================================================================
# Paquete Mara 14.10
#===============================================================================
class BaseMaraStruct(Struct):
    def _parse(self, stream, context):
        # TODO: Check checksum
        return super(BaseMaraStruct, self)._parse(stream, context)

    def _build(self, obj, stream, context):
        '''Builds frame'''
        # This code ain't no pythonic, shall make it better some time...
        obj.setdefault('sof', constants.SOF)
        obj.setdefault('length', 0) # Don't care right now
        obj.setdefault('bcc', 0)    # Don't care right now
        #=================================================================================
        # TODO: Don't rely on this payloads
        #=================================================================================
        obj.setdefault('peh', None)
        obj.setdefault('payload_10', None)

        super(BaseMaraStruct, self)._build(obj, stream, context) # stream is an I/O var
        stream.seek(0, 2) # Go to end
        length = stream.tell() # Get length
        stream.seek(1) # Seek mara length position (second byte)
        stream.write(ULInt8('length').build(length)) # Write length as ULInt8
        stream.seek(0) # Back to the beginging
        data_to_checksum = stream.read(length - 2)
        #print map(lambda c: "%.2x" % ord(c), data_to_checksum) 
        #print stream.tell()
        stream.truncate() # Discard old checksum
        cs = make_cs_bigendian(data_to_checksum)
        stream.seek(length - 2) # Go to BCC position
        stream.write(Array(2, ULInt8('foo')).build(cs))

    @classmethod
    def pretty_print(cls, container, show_header=True, show_bcc=True):
        '''Pretty printing'''
        format_frame(container, as_hex_string=False, show_header=show_header, show_bcc=show_bcc)


MaraFrame = BaseMaraStruct('Mara',
            ULInt8('sof'),
            ULInt8('length'),
            ULInt8('dest'),
            ULInt8('source'),
            ULInt8('sequence'),
            ULInt8('command'),
            If(lambda ctx: ctx.command == 0x10,
               Optional(Payload_10),
            ),
            If(lambda ctx: ctx.command == 0x12,
               PEHAdapter(Payload_PEH),
            ),
            ULInt16('bcc')
)


def ints2buffer(hexstr):
    '''
    '''
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
#aa
def dtime2dict(dtime=None):
    '''
    Converts a datetime.datetime instance into
    a dictionary suitable for ENERGY event
    timestamp
    '''
    import datetime
    if not dtime:
        dtime = datetime.datetime.now()
    d = {}
    d['year'] = dtime.year % 100
    d['month'] = dtime.month
    d['day'] = dtime.day
    d['hour'] = dtime.hour
    d['minute'] = dtime.minute
    d['second'] = dtime.second
    # Ticks de cristal que va de 0 a 32K-1 en un segundo
    d['subsec'] = float(dtime.microsecond) / 1000000
    return d


def build_frame(obj, subcon=MaraFrame):
    '''Generates a mara frame, with checksum and qty'''
    stream = subcon.build(obj)
    data = "".join([
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

def format_frame(buff, as_hex_string=False, show_header=True, show_bcc=True):

    if isinstance(buff, Container):
        d = buff
    else:
        d = parse_frame(buff, as_hex_string)
    if show_header:
        print "SOF:", d.sof
        print "QTY:", d.length
        print "DST:", d.dest
        print "SRC:", d.source
        print "SEQ:", d.sequence
        print "CMD:", d.command
    # Payload
    if d.payload_10:
        p = d.payload_10
        print "%12s" % "CANVARSYS:", p.canvarsys, "%d valores de word de 16" % (p.canvarsys / 2)
        print "%12s" % "VARSYS:", p.varsys
        print "%12s" % "CANDIS:", p.candis, "%d valores de word de 16" % (p.candis / 2)
        print "%12s" % "DIS:", p.dis
        print "%12s" % "CANAIS:", p.candis, "%d valores de word de 16" % (p.canais / 2)
        print "%12s" % "AIS:", p.ais
        # Eventos
        print "%12s" % "CANEVS:", p.canevs, "%d cada evento ocupa 10 bytes" % (p.canevs / 10)
        for ev in p.event:
            if ev.evtype == "DIGITAL":
                print '\t',
                print "DIGITAL",
                print "Q:", ev.q,
                print "ADDR485", ev.addr485,
                print "BIT: %2d" % ev.bit,
                print "PORT:", ev.port,
                print "STATUS:", ev.status,
                print "%d/%d/%d %2d:%.2d:%2.2f" % (ev.year + 2000, ev.month, ev.day, ev.hour, ev.minute, ev.second + ev.subsec)
                #print "%.2f" % ev.subsec


            elif ev.evtype == "ENERGY":
                print "\t",
                print "ENERGY Q: %d" % ev.q,
                print "ADDR485: %d" % ev.q, ev.addr485,
                print "CHANNEL: %d" % ev.channel,
                print "%d/%d/%d %2d:%.2d:%.2d" % (ev.year + 2000, ev.month, ev.day, ev.hour, ev.minute, ev.second),
                print "Value: %d Q: %d" % (ev.value.val, ev.value.q)
            else:
                print "Tipo de evento no reconocido"

    if show_bcc:
        print "BCC:", d.bcc


int2str = lambda l: ''.join(map(chr, l))




