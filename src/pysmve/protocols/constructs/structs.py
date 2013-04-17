# encoding: utf-8
#===============================================================================
# Mara Protocol Structures
#===============================================================================
from construct import *
from datetime import datetime
from ..utils.checksum import make_cs_bigendian
from .. import constants
from operator import add
from struct import pack

#===============================================================================
# Mara protocol SubConstructs
#===============================================================================

TCD = BitStruct('TCD',
                Enum(
                BitField("evtype", 2),
                DIGITAL=0,
                ENERGY=1,
                # Evento no definido aún
                IDLE=2,
                # Eventos de diagnóstico
                COMSYS=3,
                ),
                BitField("q", 2),
                BitField("addr485", 4),
                )

#=========================================================================================
# Old Bit Port Status
# Deprecated since mara 1.4v11
#=========================================================================================
#
# BPE = BitStruct('BPE',
#                 BitField("bit", 4),
#                 BitField("port", 3),
#                 BitField("status", 1),
#                 )

# Segundo byte de del evento digital
EPB = BitStruct('BPE',
                BitField("status", 1),
                BitField("port", 3),
                BitField("bit", 4),
                )

# Segundo byte del evento de energía
CodeCan = BitStruct('idlecan',
                    BitField('idle', 2),
                    BitField('code', 3),
                    BitField('channel', 3)
                    )

# Segudno byte del evento IDLE
CodeIdle = BitStruct('codeidle',
                    BitField('idle', 2),
                    BitField('code', 3),
                    BitField('idle2', 3)
                    )

# Segundo byte del evento de diangóstico
CodeMotiv = BitStruct('codemotiv',
                    BitField('code', 4),
                    BitField('motiv', 4),
                    )

TimerTicks = Struct('ticks',
                    # UBInt8('cseg'),
                    # UBInt8('dmseg'),
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
GenericTimeStamp = Struct('generic_time_stamp',
    Byte('year'),
    Byte('month'),
    Byte('day'),
    Byte('hour'),
    Byte('minute'),
)


GenericEventTail = Struct('generic_event_tail',
                                Embed(GenericTimeStamp),
                                Byte('second'),
                                UBInt16('fraction')
                                )

SECONDS_FRACTION = 2 ** 15


def container_to_datetime(obj):
    '''
    year, month, day, hour, minute, second, faction -> datetime instance
    Función auxiliar debido a que los adapters no funcionan como tales cuando están
    embebidos y para no crear una función extra'''
    fraction = obj.fraction % SECONDS_FRACTION
    microseconds = float(fraction) / SECONDS_FRACTION * 1000000
    return datetime(obj.year + 2000, obj.month, obj.day, obj.hour, obj.minute,
                        obj.second, int(microseconds))


class GenericEventTailAdapter(Adapter):
    '''Adapter para loe eventos'''
    def _decode(self, obj, context):
        return container_to_datetime(obj)

    def _encode(self, obj, context):
        obj = obj.timestamp
        fraction = obj.microsecond * (SECONDS_FRACTION / float(1000000))
        return Container(year=obj.year - 2000, month=obj.month, day=obj.day,
                         hour=obj.hour, minute=obj.minute, second=obj.second,
                         fraction=int(fraction))

EnergyEventTail = Struct('energy_event_tail',
    Embed(GenericTimeStamp),
    Array(3, Byte('data'))
)


class EnergyEventTailAdapter(Adapter):

    def _decode(self, obj, context):
        timestamp = datetime(obj.year + 2000, obj.month, obj.day, obj.hour, obj.minute,)
        data = obj.data
        data.reverse()
        value = reduce(add, map(lambda (e, v): v << 8 * e, enumerate(data)))
        return Container(timestamp=timestamp, value=value)

    def _encode(self, obj, context):
        dtime = obj['timestamp']
        data = map(ord, tuple(pack('!I', obj['value']))[1:])
        return Container(year=dtime.year - 2000, month=dtime.month, day=dtime.day,
                         hour=dtime.hour, minute=dtime.minute, data=data)


Event = Struct("event",
    Embed(TCD),
    Switch("evdetail", lambda ctx: ctx.evtype,
        {
            "DIGITAL": Embed(EPB),
            "ENERGY":  Embed(CodeCan),
            "IDLE":    Embed(CodeIdle),
            "COMSYS":  Embed(CodeMotiv),
        }
    ),
    Switch('tail', lambda ctx: ctx.evtype, {
        'ENERGY':   Embed(EnergyEventTailAdapter(EnergyEventTail)),
        'DIGITAL':  Embed(GenericEventTailAdapter(GenericEventTail)),
        'IDLE':     Embed(GenericEventTailAdapter(GenericEventTail)),
        'COMSYS':   Embed(GenericEventTailAdapter(GenericEventTail)),
        }
    ) # Switch
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


class EnergyValueAdapter(Adapter):
    """Energy qualifier is stored in it's first two bits"""
    MAX_ENERGY_VALUE = 2 ** 15  # Sganas in crescendo?olo 14 bits posibles
    MAX_Q_VALUE = 5  # Solo 5 bits

    def _encode(self, obj, context):
        '''Validates input values'''
        try:
            val, q = obj['val'], obj['q']
        except (AttributeError, TypeError):
            raise ValueError("Can't get item 'val' or 'q' from %s, is it a construct.Container?" % obj)
        assert 0 <= val < self.MAX_ENERGY_VALUE
        assert 0 <= q <= self.MAX_Q_VALUE
        data = bitfield(0)
        data[0:14] = obj['val']
        data[14:16] = obj['q']
        return int(data)

    def _decode(self, int_val, context):
        data = bitfield(int_val)
        retval = Container(val=data[0:14], q=data[14:16])
        return retval


class MaraDateTimeAdapter(Adapter):
    '''
    Mara bytes <--> datetime.datetime
    '''
    def _decode(self, obj, context):
        return datetime(obj.year + 2000, obj.month, obj.day, obj.hour, obj.minute, obj.second)

    def _encode(self, obj, context):
        return Container(year=obj.year - 2000, month=obj.month, day=obj.day,
                         hour=obj.hour, minute=obj.minute, second=obj.second)


class SubSecondAdapter(Adapter):
    '''Mara timestamp sub-second data is measured in 1/32 second steps,
    and its value is given by a counter which goes from 0 to 0x7FFF'''

    FRACTIONS = 2 ** 14

    def _encode(self, obj, context):
        return int(obj * self.FRACTIONS)

    def _decode(self, obj, context):
        K = 1
        return obj * K / float(self.FRACTIONS)


class PEHAdapter(Adapter):
    def _decode(self, obj, context):
        return datetime(obj.year + 2000, obj.month, obj.day, obj.hour, obj.minute, obj.second)

    def _encode(self, obj, context):
        '''bytes->datetime'''
        return Container(year=obj.year - 2000, month=obj.month, day=obj.day,
                         hour=obj.hour, minute=obj.minute, second=obj.second,
                         fsegh=0, fsegl=0,
                         day_of_week=obj.weekday(),
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
        obj.setdefault('length', 0)  # Don't care right now
        obj.setdefault('bcc', 0)    # Don't care right now
        #=================================================================================
        # TODO: Don't rely on this payloads
        #=================================================================================
        obj.setdefault('peh', None)
        obj.setdefault('payload_10', None)

        super(BaseMaraStruct, self)._build(obj, stream, context)  # stream is an I/O var
        stream.seek(0, 2)  # Go to end
        length = stream.tell()  # Get length
        stream.seek(1)  # Seek mara length position (second byte)
        stream.write(ULInt8('length').build(length))  # Write length as ULInt8
        stream.seek(0)  # Back to the beginging
        data_to_checksum = stream.read(length - 2)
        # print map(lambda c: "%.2x" % ord(c), data_to_checksum)
        # print stream.tell()
        stream.truncate()  # Discard old checksum
        cs = make_cs_bigendian(data_to_checksum)
        stream.seek(length - 2)  # Go to BCC position
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
            #Probe(),

            If(lambda ctx: ctx.command == 0x10,
               #Probe(),
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
    parts = [chr(an_int) for an_int in hexstr]
    return ''.join(parts)


def hexstr2buffer(a_str):
    '''
    "FE  01" => '\xFE\x01'
    '''
    import re
    a_str = a_str.strip().replace('\n', ' ')
    a_list = [chr(int(bytestr, 16)) for bytestr in re.split('[:\s]', a_str) if len(bytestr)]
    return ''.join(a_list)


def any2buffer(data):
    if isinstance(data, list):
        return ints2buffer(data)
    elif isinstance(data, basestring):
        return hexstr2buffer(data)
    raise Exception("%s can't be converted to string buffer")

# Buffer -> Upper Human Readable Hex String
upperhexstr = lambda buff: ' '.join([("%.2x" % ord(c)).upper() for c in buff])
# aa


def dtime2dict(dtime=None):
    '''
    Converts a datetime.datetime instance into
    a dictionary suitable for ENERGY event
    timestamp
    '''
    if not dtime:
        dtime = datetime.now()
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
                print "%d/%d/%d %2d:%.2d:%2.2f" % (ev.year + 2000, ev.month, ev.day, ev.hour,
                                                   ev.minute, ev.second + ev.fraction)
                # print "%.2f" % ev.subsec

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


