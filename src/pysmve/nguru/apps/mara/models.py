# encoding: utf-8
import operator
from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from protocols import constants
# from jsonfield import JSONField
from datetime import datetime, time


class Profile(models.Model):
    name = models.CharField(max_length=80)
    version = models.IntegerField(default=1)
    default = models.BooleanField()

    def __unicode__(self):
        return "'%s' v.%s" % (self.name, self.version)

    def clone(self):
        '''Clone profile'''
        raise NotImplementedError("Not implemented yet")

    class Meta:
        unique_together = (('name', 'version'))

    @classmethod
    def ensure_default(cls, instance, **kwargs):
        '''Signal handler to ensure default profile'''
        if not instance.pk:
            if instance.default:
                # New instance wants to be default
                cls.objects.update(default=False)
            else:
                # Does not want to be default, the only one?
                if cls.objects.count() == 0:
                    instance.default = True
    a = True
signals.pre_save.connect(Profile.ensure_default, sender=Profile)


class COMaster(models.Model):

    '''
    A gateway with mara IEDs that also performs other
    tasks such time synchronization with slaves.
    '''
    profile = models.ForeignKey(Profile,
                                related_name='comasters')
    ip_address = models.IPAddressField()
    enabled = models.BooleanField(default=False)
    port = models.IntegerField(verbose_name="TCP port for connection",
                               default=constants.DEFAULT_COMASTER_PORT)
    # ------------------------------------------------------------------------------------
    # Timing values
    # ------------------------------------------------------------------------------------
    poll_interval = models.FloatField(verbose_name="Poll interval in seconds",
                                      default=5)
    exponential_backoff = models.BooleanField(default=False,
                                              help_text="Make queries")

    max_retry_before_offline = models.IntegerField(default=3)

    sequence = models.IntegerField(help_text=u"Current sequence number",
                                   default=0)

    rs485_source = models.SmallIntegerField(
        default=0,
        help_text='RS485 source address'
    )
    rs485_destination = models.SmallIntegerField(default=0)

    process_pid = models.IntegerField(blank=True, null=True,
                                      default=None,
                                      editable=False,
                                      help_text="PID del proceso que se encuentra utilizando el proceso")

    peh_time = models.TimeField(default=time(1, 0, 0),
                                help_text="Tiempo entre puesta en hora")

    @property
    def dis(self):
        dis = DI.objects.filter(ied__co_master=self)
        dis = dis.order_by('ied__offset', 'port', 'bit')
        return dis

    @property
    def ais(self):
        ais = AI.objects.filter(ied__co_master=self)
        ais = ais.order_by('ied__offset', 'offset')
        print ais.count()
        return ais

    @property
    def svs(self):
        svs = SV.objects.filter(ied__co_master=self)
        svs = svs.order_by('ied', 'offset', 'bit')
        return svs

    def __unicode__(self):
        return u"%s" % self.ip_address

    class Meta:
        verbose_name = "CO Master"
        verbose_name_plural = "CO Masters"


class IED(models.Model):

    '''
    Inteligent Electronic Device.
    '''
    co_master = models.ForeignKey(COMaster, related_name='ieds')
    offset = models.SmallIntegerField(default=0)
    rs485_address = models.SmallIntegerField(default=0)

    def __unicode__(self):
        return u"%s:IED:%s" % (self.co_master.ip_address, self.rs485_address)

    class Meta:
        verbose_name = "IED"
        verbose_name_plural = "IEDs"
        unique_together = ('co_master', 'rs485_address')
        ordering = ('offset',)

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
    offset = models.SmallIntegerField(default=0,
                                      verbose_name="Byte offset in mara frame")
    param = models.CharField(max_length=50,
                             null=True,
                             blank=True)
    last_update = models.DateTimeField(blank=True, null=True)

    description = models.CharField(max_length=100,
                                   null=True,
                                   blank=True
                                   )
    trasducer = models.CharField(max_length=50, null=True, blank=True)

    tag = models.CharField(max_length=16)

    def __unicode__(self):
        return "%s %s" % (self.param, self.description or '')

    class Meta:
        abstract = True

    def update_value(self, value, timestamp=None, q=None):
        self.value = value
        if not timestamp:
            timestamp = datetime.now()
        self.last_update = timestamp
        # TODO: Emit singal
        self.save()


class SV(MV):

    '''
    System variable
    '''
    BIT_CHOICES = [(None, 'Palabra Completa'), ] + [(n, 'Bit %d' % n) for n in range(8)]
    bit = models.IntegerField(default=0, null=True, blank=True, choices=BIT_CHOICES)
    value = models.IntegerField(default=0)

    class Meta:
        unique_together = ('offset', 'ied', 'bit')
        verbose_name = "System Variable"
        verbose_name_plural = "System Variables"
        # Default ordering
        ordering = ('ied__offset', 'offset')

    BIT = 1
    BYTE = 8
    # TODO Optimize
    @property
    def width(self):
        '''Returns width 1 or 8'''
        sv_in_same_offset = self.ied.sv_set.filter(offset=self.offset)
        if sv_in_same_offset == 8:
            return self.BIT
        else:
            return self.BYTE


class DI(MV):

    '''
    Digital input, each row represents a bit in a port
    Every port is virtualized in mara device
    '''
    port = models.IntegerField(default=0)
    bit = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    q = models.IntegerField(default=0)
    maskinv = models.IntegerField(default=0)
    nrodi = models.IntegerField(default=0)
    idtextoev2 = models.IntegerField(default=0)
    persoaccinoh = models.IntegerField(default=0)
    pesoaccionl = models.IntegerField(default=0)


    def __unicode__(self):
        return u"DI %2d:%2d (%s)" % (self.port, self.bit, (self.tag or "Sin Tag"))

    class Meta:
        unique_together = ('offset', 'ied', 'port', 'bit')
        ordering = ('port', 'bit')
        verbose_name = "Digital Input"
        verbose_name_plural = "Digital Inputs"


class GenericEvent(models.Model):

    """Clase genérica que agrupa a todos los eventos
    """
    timestamp = models.DateTimeField()
    timestamp_ack = models.DateTimeField(null=True, blank=True, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, editable=False)

    def descripcion(self):
        '''Retorna la descripción'''
        return None

    class Meta:
        abstract = True


class Event(models.Model):

    '''
    Digital Event, it's always related with a bit and a port.
    '''
    di = models.ForeignKey(DI, related_name='events')
    timestamp = models.DateTimeField()
    timestamp_ack = models.DateTimeField(null=True, blank=True, )
    q = models.IntegerField()
    value = models.IntegerField()


class ComEventKind(models.Model):

    '''Gives a type to communication event'''
    code = models.IntegerField()
    description = models.CharField(max_length=50)
    texto_2 = models.IntegerField()
    pesoaccion = models.IntegerField()

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = 'com'
        ordering = ('code', )


class ComEvent(GenericEvent):
    ied = models.ForeignKey(IED)
    kind = models.ForeignKey(ComEventKind)
    motiv = models.IntegerField()

    @property
    def description(self):
        return self.kind.description

    class Meta:
        db_table = 'eventcom'



class AI(MV):
    '''
    Analog Input
    '''
    channel = models.IntegerField(default=0)
    unit = models.CharField(max_length=5)
    multip_asm = models.FloatField(default=1.09)
    divider = models.FloatField(default=1)
    rel_tv = models.FloatField(db_column="reltv", default=1)
    rel_ti = models.FloatField(db_column="relti", default=1)
    rel_33_13 = models.FloatField(db_column="rel33-13", default=1)
    q = models.IntegerField(db_column="q", default=0)
    value = models.SmallIntegerField(default=-1)

    escala = models.FloatField(help_text="Precalculo de multip_asm, divider, reltv, "
                               "relti y rel33-13", default=0)

    noroai = models.IntegerField(default=0)
    idtextoevm = models.IntegerField(null=True, blank=True)

    value_max = models.IntegerField(null=True, blank=True)
    value_min = models.IntegerField(null=True, blank=True)
    delta_h = models.IntegerField(null=True, blank=True)
    delta_l = models.IntegerField(null=True, blank=True)
    pesoaccion_h = models.IntegerField(null=True, blank=True)
    pesoaccion_l = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('offset', 'ied',)
        verbose_name = "Analog Input"
        verbose_name_plural = "Analog Inputs"

    def human_value(self):
        values = [self.multip_asm,
                  self.divider,
                  self.rel_tv,
                  self.rel_ti,
                  self.rel_33_13,
                  self.value
                  ]
        return "%.2f %s" % (reduce(operator.mul, values), self.unit)


class Energy(models.Model):
    '''
    Energy Measure. Every day has 96 energy values taken from the energy meter
    '''
    ai = models.ForeignKey(AI)

    timestamp = models.DateTimeField()
    value = models.IntegerField()
    code = models.IntegerField()
    hnn = models.BooleanField(help_text='Hora no normalizada', default=False)
    q = models.IntegerField(verbose_name="Quality")

    class Meta:
        verbose_name = "Energy Measure"
        verbose_name_plural = "Energy Measures"

