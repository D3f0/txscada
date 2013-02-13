
from construct import *
from datetime import datetime
from operator import add

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

class GenericEventTailAdapter(Adapter):

    SECONDS_FRACTION = 2 ** 15

    def _decode(self, obj, context):
        fraction = obj.fraction % self.SECONDS_FRACTION
        microseconds = float(fraction) / self.SECONDS_FRACTION * 1000000
        return datetime(obj.year + 2000, obj.month, obj.day, obj.hour, obj.minute,
                        obj.second, int(microseconds))

    def _encode(self, obj, context):
        fraction = obj.microsecond * (self.SECONDS_FRACTION / float(1000000))
        return Container(year=obj.year - 2000, month=obj.month, day=obj.day,
                         hour=obj.hour, minute=obj.minute, second=obj.second,
                         fraction=int(fraction))

EnergyEventTail = Struct('energy_event_tail',
    Embed(GenericTimeStamp),
    Array(3, Byte('data'))
)

class EnergyEventTailAdapter(Adapter):

    def _decode(self, obj, context):
        daystamp = datetime(obj.year + 2000, obj.month, obj.day, obj.hour, obj.minute,)
        data = obj.data
        data.reverse()
        value = reduce(add, map(lambda (e, v): v << 8 * e, enumerate(data)))
        return {'datetime': daystamp, 'value': value}

    def _encode(self, obj, context):
        assert hasattr(obj, 'datetime') and hasattr(obj, 'value'), "Missing data"

        return Container(year=obj.year - 2000, month=obj.month, day=obj.day,
                         hour=obj.hour, minute=obj.minute, data=data)

#
def str2hexa(data):
    '''Raw data to hex representation'''
    data = ' '.join([ '%.2x' % ord(x) for x in str(data)])
    return data.upper()


value = '\x08\x01\x0B\x11\x30\x01\x40\x00'
adp = GenericEventTailAdapter(GenericEventTail)
v = adp.parse(value)
print v
print str2hexa(adp.build(datetime.now()))

print EnergyEventTailAdapter(EnergyEventTail).parse(value[:-3]+'\x02\x01\xFF')
