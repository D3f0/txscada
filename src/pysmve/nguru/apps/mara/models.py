# encoding: utf-8

import operator
from datetime import datetime, time
from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
# from jsonfield import JSONField
from django.utils.translation import ugettext as _
from protocols.utils.bitfield import iterbits
from protocols import constants
from protocols.utils.words import expand
from protocols.constructs.structs import container_to_datetime


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
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

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

    def load_tags(self, *largs, **kwargs):
        '''Can be hooked'''
        tags = {}
        dis = DI.objects.filter(ied__co_master__profile=self)
        ais = AI.objects.filter(ied__co_master__profile=self)
        tags.update(**dict(dis.values_list('tag', 'description')))
        tags.update(**dict(ais.values_list('tag', 'description')))
        return tags

    _tag_info = {}
    def tag_description(self, tag, empty_text=''):
        if not self.pk in Profile._tag_info:
            Profile._tag_info[self.pk] = self.load_tags()
        return Profile._tag_info[self.pk].get(tag, empty_text)

    __tags = None
    @property
    def tags(self):
        if not self.__tags:
            self.__tags = self.load_tags()
        return self.__tags

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
    # ------------------------------------------------------------------------
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
        dis = dis.order_by('ied__offset', 'offset', 'port', 'bit')
        return dis

    @property
    def ais(self):
        ais = AI.objects.filter(ied__co_master=self)
        ais = ais.order_by('ied__offset', 'offset')
        return ais

    @property
    def svs(self):
        svs = SV.objects.filter(ied__co_master=self)
        svs = svs.order_by('ied__offset', 'offset', 'bit')
        return svs

    def __unicode__(self):
        return u"%s" % self.ip_address

    class Meta:
        verbose_name = _("CO Master")
        verbose_name_plural = _("CO Masters")

    def process_frame(self, mara_frame):
        '''Takes a Mara frame and saves it into the DB model'''
        payload = getattr(mara_frame, 'payload_10', None)
        if not payload:
            raise ValueError(
                _("Mara payload not present. %s does not look like a frame") %
                mara_frame
            )
        # Some counters
        di_count, ai_count, sv_count, event_count = 0, 0, 0, 0
        t0, timestamp = time(), datetime.now()
        for value, di in zip(iterbits(payload.dis, length=16), self.dis):
            # Poener en 0 en
            di.update_value(value, q=0, last_update=timestamp)
            di_count += 1
        for value, ai in zip(payload.ais, self.ais):
            # TODO: Copiar Q
            ai.update_value(value, last_update=timestamp)
            ai_count += 1

        variable_widths = [v.width for v in self.svs]

        for value, sv in zip(expand(payload.varsys, variable_widths), self.svs):
            sv.update_value(value, last_update=timestamp)
            sv_count += 1

        for event in payload.event:
            if event.evtype == 'DIGITAL':
                # Los eventos digitales van con una DI
                try:
                    di = DI.objects.get(
                                        ied__rs485_address=event.addr485,
                                        ied__co_master=self,
                                        port=event.port,
                                        bit=event.bit)
                    di.events.create(
                        timestamp=container_to_datetime(event),
                        q=event.q,
                        value=event.status
                    )
                    print "Evento recibido de", di.port, di.bit
                except DI.DoesNotExist:
                    print "Evento para una DI que no existe!!!"
            elif event.evtype == 'ENERGY':
                try:
                    query = dict(
                        ied__rs485_address=event.addr485,
                        ied__co_master=self,
                        channel=event.channel,
                    )
                    ai = AI.objects.get(**query)
                    timestamp = container_to_datetime(event)
                    value = 0
                    for i, v in enumerate(event.data):
                        value += v << (8 * i)
                    ai.energy_set.create(
                        timestamp=timestamp,
                        code=event.code,
                        q=event.q,
                        hnn=event.hnn,
                        value=value
                    )
                except AI.DoesNotExist:
                    print "Medicion de energia no reconcible", event
                except AI.MultipleObjectsReturned:
                    print "Demaciadas AI con ", query
            elif event.evtype == 'COMSYS':
                try:
                    ied = self.ieds.get(rs485_address=event.addr485)
                    timestamp = container_to_datetime(event)
                    try:
                        kind = ComEventKind.objects.get(code=event.code)
                    except ComEventKind.DoesNotExist:
                        kind = None
                    ied.comevent_set.create(
                        kind=kind,
                        motiv=event.motiv,
                        timestamp=timestamp
                    )
                except ComEvent.DoesNotExist:
                    print "No se puede crear el Evento tipo 3"
        from apps.hmi.models import Formula
        Formula.calculate()
        return di_count, ai_count, sv_count, event_count

    def set_ai_quality(self, value):
        pass

    def set_sv_quality(self, value):
        pass

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
        verbose_name = _("IED")
        verbose_name_plural = _("IEDs")
        unique_together = ('co_master', 'rs485_address')
        ordering = ('offset',)

    def create_dis(self, ports, bit_width=16):
        for port in range(0, ports):
            for bit in range(0, bit_width):
                param = "D%.2d" % ((port * self.PORT_WIDTH) + bit)
                self.ied_set.create(port=port, bit=bit, param=param)


class MV(models.Model):
    '''
    IEC Meassured Value
    '''
    # These attributes will also be sent when a model is updated
    EXTRA_WATCHED_ATTRIBUTES = ('pk', 'tag')

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

    def update_value(self, value, **kwargs):
        '''Actualiza el valor'''
        self.value = value

        self.last_update = kwargs.pop('last_update', datetime.now())
        for k, v in kwargs.items():
            setattr(self, k, v)
        # TODO: Emit singal
        self.save()


class SV(MV):

    '''
    System variable
    '''
    WATCHED_FIELDS = ('value', )

    BIT_CHOICES = [(None, 'Palabra Completa'), ] + [(n, 'Bit %d' % n)
                                                    for n in range(8)]
    bit = models.IntegerField(
        default=0, null=True, blank=True, choices=BIT_CHOICES)
    value = models.IntegerField(default=0)

    class Meta:
        unique_together = ('offset', 'ied', 'bit')
        verbose_name = _("System Variable")
        verbose_name_plural = _("System Variables")
        # Default ordering
        ordering = ('ied__offset', 'offset')

    BIT = 1
    BYTE = 8
    # TODO Optimize

    @property
    def width(self):
        '''Returns width 1 or 8'''
        try:
            self.ied.sv_set.get(offset=self.offset, bit=2)
            return self.BIT
        except SV.DoesNotExist:
            return self.BYTE



class DI(MV):

    '''
    Digital input, each row represents a bit in a port
    Every port is virtualized in mara device
    '''
    WATCHED_FIELDS = ('value', )

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
        verbose_name = _("Digital Input")
        verbose_name_plural = _("Digital Inputs")

    @classmethod
    def check_value_change(cls, instance=None, **kwargs):
        if instance.pk:
            old_value = DI.objects.get(pk=instance.pk).value
            if old_value != instance.value:
                print "%s change from %s -> %s at %s" % (instance,
                                                         old_value,
                                                         instance.value,
                                                         instance.last_update)

signals.pre_save.connect(DI.check_value_change, sender=DI)


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

    def __unicode__(self):
        text2 = None
        kinds = EventKind.objects.filter(idtextoev2=self.di.idtextoev2)
        if kinds.filter(value=self.value).count() == 1:
            try:
                text2 = kinds.get(value=self.value).text
            except EventKind.DoesNotExist:
                text2 = kinds.get().text
        return "%s %s" % (self.di.description or "No description", text2 or "No Text 2")

    class Meta:
        verbose_name = _("Event")
        verbose_name = _("Events")


class EventKind(models.Model):
    '''Abstracción de textoev2'''
    text = models.CharField(max_length=50)
    value = models.IntegerField(blank=True, null=True)
    idtextoev2 = models.IntegerField()
    class Meta:
        unique_together = ('idtextoev2', 'value')
        verbose_name = _("Event Kind")
        verbose_name = _("Event Kinds")

    def __unicode__(self):
        dis = ','.join([di.description or 'Sin Descripcion' for di in
                    DI.objects.filter(idtextoev2=self.idtextoev2)])
        dis = dis or 'No DI'
        return '%s value=%s text=%s' % (dis, self.value or u'Vacio', self.text)


class ComEventKind(models.Model):
    '''Gives a type to communication event'''
    code = models.IntegerField()
    texto_2 = models.IntegerField()
    pesoaccion = models.IntegerField()

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = 'com'
        ordering = ('code', )
        verbose_name = _("Communication Event Kind")
        verbose_name = _("Communication Event Kinds")


class ComEvent(GenericEvent):
    motiv = models.IntegerField()
    ied = models.ForeignKey(IED)
    kind = models.ForeignKey(ComEventKind, blank=True, null=True)

    @property
    def description(self):
        return self.kind.description

    def __unicode__(self):
        if not self.kind:
            return "No description"
        else:
            return EventKind.objects.get(idtextoev2=self.kind.texto_2)

    class Meta:
        db_table = 'eventcom'
        verbose_name = _("Communication Event")
        verbose_name_plural = _("Communication Events")


class AI(MV):

    '''
    Analog Input
    '''
    WATCHED_FIELDS = ('value', )

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
        verbose_name = _("Analog Input")
        verbose_name_plural = _("Analog Inputs")

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
        verbose_name = _("Energy Measure")
        verbose_name_plural = _("Energy Measures")


class Action(models.Model):
    bit = models.IntegerField()
    descripcion = models.CharField(max_length=50)
    script = models.CharField(max_length=50)
    argumentos = models.CharField(max_length=50)

    @classmethod
    def get_actions_for_peso(cls, peso):
        bit_values = []
        for i in range(32):
            bit_val = 1 << i
            if peso & bit_val:
                bit_values.append(bit_val)
        return cls.objects.filter(bit__in=bit_values)

    def __unicode__(self):
        return self.descripcion

    class Meta:
        unique_together = ('bit', )
        verbose_name = _("Action")
        verbose_name_plural = _("Actions")


def register():
    """Register model for update tracking"""
