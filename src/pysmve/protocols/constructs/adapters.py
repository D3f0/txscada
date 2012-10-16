#===============================================================================
# Adapters
#===============================================================================
from construct.core import Adapter, AdaptationError
from ..utils.bitfield import bitfield
from construct.lib.container import Container
from datetime import datetime

class EnergyValueAdapter(Adapter):
    """Energy qualifier is stored in it's first two bits"""
    MAX_ENERGY_VALUE = 2**15 # Sganas in crescendo?olo 14 bits posibles
    MAX_Q_VALUE = 5 # Solo 5 bits
    
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
        return datetime(obj.year+2000, obj.month, obj.day, obj.hour, obj.minute, obj.second)
    
    def _encode(self, obj, context):
        return Container(year=obj.year-2000, month=obj.month, day=obj.day, 
                         hour=obj.hour, minute=obj.minute, second=obj.second)
        
class SubSecondAdapter(Adapter):
    '''Mara timestamp sub-second data is measured in 1/32 second steps,
    and its value is given by a counter which goes from 0 to 0x7FFF'''
    def _encode(self, obj, context):
        raise AdaptationError("Cant encode yet :(")
    
    def _decode(self, obj, context):
        K = 1
        return obj * K / float(32768) 
    
    
class PEHAdapter(Adapter):
    def _decode(self, obj, context):
        return datetime(obj.year+2000, obj.month, obj.day, obj.hour, obj.minute, obj.second)
        
    
    
    def _encode(self, obj, context):
        '''bytes->datetime'''
        return Container(year=obj.year-2000, month=obj.month, day=obj.day,
                         hour=obj.hour, minute=obj.minute, second=obj.second,
                         fsegh=0, fsegl=0,
                         day_of_week = obj.weekday(),
                         )
    
    