# encoding: utf-8

from django.db import models
from protocols import constants

# Create your models here.
class Profile(models.Model):
    # Name of the 
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    # Version, something relevant for the user
    version = models.CharField(default='1', max_length=1)
    # Date of creation
    date = models.DateField(auto_now=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        unique_together = ('name',)


class COMaster(models.Model):
    '''
    A gateway with mara IEDs that also performs other
    tasks such time synchronization with slaves.
    '''
    profile = models.ForeignKey(Profile)
    ip_address = models.IPAddressField()
    enabled = models.BooleanField(default=False)
    port = models.IntegerField(verbose_name="TCP port for connection",
                               default=constants.DEFAULT_COMASTER_PORT)
    poll_interval = models.FloatField(verbose_name="Poll interval in seconds",
                                      default=5)
    sequence = models.IntegerField(help_text=u"Current sequence number")
    rs485_source = models.SmallIntegerField(
                                            default=0,
                                            help_text='RS485 source address'
                                            )
    rs485_destination = models.SmallIntegerField(default=0)

    def __unicode__(self):
        return u"%s" % self.ip_address

    class Meta:
        verbose_name = "CO Master"
        verbose_name_plural = "CO Masters"

class IED(models.Model):
    '''
    Inteligent Electronic Device.
    '''
    co_master = models.ForeignKey(COMaster)
    offset = models.SmallIntegerField(default=0)
    rs485_address = models.SmallIntegerField(default=0)


    class Meta:
        verbose_name = "IED"
        verbose_name_plural = "IEDs"
        unique_together = ('co_master', 'rs485_address')


    def create_dis(self, ports, bit_width=16):
        for port in range(0, ports):
            for bit in range(0, bit_width):
                param = "D%.2d" % ((port * self.PORT_WIDTH) + bit)
                self.ied_set.create(port=port, bit=bit, param=param)

class Unit(models.Model):
    '''
    Unit of measure
    '''
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class MV(models.Model):
    '''
    IEC Meassured Value
    '''
    ied = models.ForeignKey(IED)
    offset = models.SmallIntegerField(default=0)
    param = models.CharField(max_length=10)
    description = models.CharField(max_length=100)

    class Meta:
        abstract = True



class SV(MV):
    '''
    System variable
    '''
    unit = models.ForeignKey(Unit)
    value = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = ('offset', 'ied',)

class DI(MV):
    '''
    Digital input, each row represents a bit in a port
    Every port is virtualized in mara device
    '''
    port = models.IntegerField(default=0)
    bit = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    q = models.IntegerField(default=0)

    def __unicode__(self):
        return u"DI %2d:%2d (%s)" % (self.port, self.bit, self.param)

    class Meta:
        unique_together = ('offset', 'ied',)
        verbose_name = "Digital Input"
        verbose_name_plural = "Digital Inputs"

class Event(models.Model):
    '''
    Digital Event, it's always related with a bit and a port.
    '''
    di = models.ForeignKey(DI)
    timestamp = models.DateTimeField()
    subsecond = models.FloatField()
    q = models.IntegerField()
    value = models.IntegerField()


class AI(MV):
    '''
    Analog Input
    '''
    unit = models.ForeignKey(Unit)
    multip_asm = models.FloatField(default=1.09)
    divider = models.FloatField(default=1)
    rel_tv = models.FloatField(db_column="reltv", default=1)
    rel_ti = models.FloatField(db_column="relti", default=1)
    rel_33_13 = models.FloatField(db_column="rel33-13", default=1)
    q = models.IntegerField(db_column="calif", default=0)

    class Meta:
        unique_together = ('offset', 'ied',)
        verbose_name = "Analog Input"
        verbose_name_plural = "Analog Inputs"

class Energy(MV):
    '''
    Energy Measure. Every day has 96 energy values taken from the energy meter
    '''
    #ied = models.ForeignKey(IED)
    #offset = models.IntegerField()
    #param = models.CharField()
    #description = models.CharField()
    address = models.IntegerField(default=0)
    channel = models.IntegerField(default=0)
    unit = models.ForeignKey(Unit)
    Ke = models.FloatField(default=1)
    divider = models.FloatField(default=1)
    rel_tv = models.FloatField(default=1)
    rel_ti = models.FloatField(default=1)
    rel_33_13 = models.FloatField(default=1)
    timestamp = models.DateTimeField()
    value = models.IntegerField()
    q = models.IntegerField(verbose_name="Quality")


    class Meta:
        verbose_name = "Energy Measure"
        verbose_name_plural = "Energy Measures"
