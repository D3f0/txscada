# encoding: utf-8

import operator
from datetime import datetime, time
from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from apps.mara.utils import get_relation_managers
# from jsonfield import JSONField
from django.utils.translation import ugettext as _
from protocols.utils.bitfield import iterbits
from protocols import constants
from protocols.utils.words import expand
from protocols.constructs.structs import container_to_datetime
from utils import ExcelImportMixin, counted


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

    @classmethod
    def get_profile(cls, name, clear=False):

        """Returns a profile"""

        profile, created = cls.objects.get_or_create(
            name=name)

        if not created and clear:
            for manager in get_relation_managers(profile):
                manager.all().count()
                manager.all().delete()
        return profile

signals.pre_save.connect(Profile.ensure_default, sender=Profile)


class COMaster(models.Model, ExcelImportMixin):

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
            value = value & 0x0FFF
            ai.q = (value & 0xC000) >> 14
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
        try:
            Formula.calculate()
        except Exception, e:
            print e

        return di_count, ai_count, sv_count, event_count

    def set_ai_quality(self, value):
        pass

    def set_sv_quality(self, value):
        pass

    @classmethod
    def do_import_excel(cls, workbook, models):
        """Import COMaster from excel sheet. This is the base import, does not any
        filtering."""
        fields = ('id', 'ip_address', 'port', 'enabled')
        for i, (pk, ip_address, port, enabled) in\
            enumerate(workbook.iter_as_dict('comaster', fields=fields)):

            enabled = bool(int(enabled))
            # TODO: Make imports work

            comaster = models.profile.comasters.create(id=pk,
                                                       ip_address=ip_address,
                                                       port=port,
                                                       enabled=enabled,
                                                       )
            IED.import_excel(workbook, profile=models.profile, comaster=comaster)


class IED(models.Model, ExcelImportMixin):

    '''
    Inteligent Electronic Device.
    '''
    co_master = models.ForeignKey(COMaster, related_name='ieds')
    offset = models.SmallIntegerField(default=0)
    rs485_address = models.SmallIntegerField(default=0)

    def __unicode__(self):
        return u"%s[%.2d]" % (self.co_master.ip_address, self.rs485_address)

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

    @classmethod
    def do_import_excel(cls, workbook, models):
        '''Import IED from XLS "ied" sheet. Filters IEDs belonging to comaster
        passed in models bunch'''
        fields = ('comaster_id', 'id', 'offset', 'rs485_address',)

        def ied_belongs_to_comaster(row):
            '''Row is a named tuple'''
            try:
                if int(row.comaster_id) != models.comaster.pk:
                    return False
            except ValueError:
                return False
            return True

        for n, (comaster_id, pk, offset, rs485_address)\
            in enumerate(workbook.iter_as_dict('ied',
                                               fields=fields,
                                               row_filter=ied_belongs_to_comaster)):

            ied = models.comaster.ieds.create(
                offset=offset,
                rs485_address=rs485_address,
                pk=pk,
            )
            DI.import_excel(workbook, ied=ied)
            AI.import_excel(workbook, ied=ied)
            SV.import_excel(workbook, ied=ied)


class MV(models.Model):

    """Base class for measured values, and Mara main structure"""
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


class SV(MV, ExcelImportMixin):

    '''
    System variable
    '''
    WATCHED_FIELDS = ('value',)

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

    @classmethod
    def do_import_excel(cls, workbook, models):
        """Import SV (System Variables) from excel sheet"""
        fields = "ied_id    offset  bit param   description value".split()
        def sv_belongs_to_ied(row):
            try:
                if (row.ied_id) != models.ied.pk:
                    return False
            except ValueError:
                return False
            return True

        for (ied_id, offset, bit, param, description, value)\
            in workbook.iter_as_dict('varsys',
                                     fields=fields,
                                     row_filter=sv_belongs_to_ied):
            models.ied.sv_set.create(
                offset=offset,
                bit=bit,
                param=param,
                description=description,
                value=value or 0
            )




class DI(MV, ExcelImportMixin):

    '''
    Digital input, each row represents a bit in a port
    Every port is virtualized in mara device
    '''
    WATCHED_FIELDS = ('value',)

    port = models.IntegerField(default=0)
    bit = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    q = models.IntegerField(default=0)
    maskinv = models.IntegerField(default=0)
    nrodi = models.IntegerField(default=0)
    idtextoev2 = models.IntegerField(default=0)
    pesoaccion_h = models.IntegerField(default=0)
    pesoaccion_l = models.IntegerField(default=0)

    def __unicode__(self):
        return u"DI %2d:%2d (%s)" % (self.port, self.bit, (self.tag or "Sin Tag"))

    class Meta:
        unique_together = ('offset', 'ied', 'port', 'bit')
        ordering = ('port', 'bit')
        verbose_name = _("Digital Input")
        verbose_name_plural = _("Digital Inputs")

    @classmethod
    def check_value_change(cls, instance=None, **kwargs):
        try:
            if instance.pk:
                old_value = DI.objects.get(pk=instance.pk).value
                if old_value != instance.value:
                    print "%s change from %s -> %s at %s" % (instance,
                                                             old_value,
                                                             instance.value,
                                                             instance.last_update)
        except Exception, e:
            print e
    @classmethod
    def do_import_excel(cls, workbook, models):
         """Import DI for IED from XLS di sheet"""

         def di_belongs_to_ied(row):
            try:
                if int(row.ied_id) != models.ied.pk:
                    return False
            except ValueError:
                return False
            return True

         fields = (
                    'id',
                    'ied_id',
                    'tag',
                    'port',
                    'bit',
                    'value',
                    'q',
                    'trasducer',
                    'maskinv',
                    'description',
                    'idtextoev2',
                    'pesoaccionh',
                    'pesoaccionl'
                )
         for i, (pk, ied_id, tag, port, bit, value, q, trasducer, maskinv, description,
                idtextoev2, pesoaccion_h, pesoaccion_l)\
            in enumerate(workbook.iter_as_dict('di',
                                               fields=fields,
                                               row_filter=di_belongs_to_ied)):

            models.ied.di_set.create(
                pk=pk,
                tag=tag,
                port=port,
                bit=bit,
                value=value,
                q=q,
                trasducer=trasducer,
                maskinv=maskinv,
                description=description,
                idtextoev2=idtextoev2 or 0,
                pesoaccion_h=pesoaccion_h or 0,
                pesoaccion_l=pesoaccion_l or 0,
            )

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
    timestamp_ack = models.DateTimeField(null=True, blank=True,)
    q = models.IntegerField()
    value = models.IntegerField()

    def __unicode__(self):
        text2 = None
        kinds = EventText.objects.filter(idtextoev2=self.di.idtextoev2)
        if kinds.filter(value=self.value).count() == 1:
            try:
                text2 = kinds.get(value=self.value).text
            except EventText.DoesNotExist:
                text2 = kinds.get().text
        return "%s %s" % (self.di.description or "No description", text2 or "No Text 2")

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")




class EventText(models.Model, ExcelImportMixin):
    '''Abstracción de textoev2'''
    profile = models.ForeignKey(Profile, related_name='event_kinds')
    description = models.CharField(max_length=50, blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    idtextoev2 = models.IntegerField(null=True, blank=True)
    # It's stored in DI
    pesoaccion = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('idtextoev2', 'value')
        verbose_name = _("Event Text")
        verbose_name_plural = _("Event Texts")

    def __unicode__(self):
        return self.description


    @classmethod
    def do_import_excel(cls, workbook, models):
        """Import text for events from XLS sheet 'com'"""
        fields = 'id    code    description idTextoEv2  pesoaccion'.lower().split()
        for pk, code, description, idtextoev2, pesoaccion in\
            workbook.iter_as_dict('com', fields=fields):
            models.profile.event_kinds.create(
                description=description,
                value=code,
                idtextoev2=idtextoev2,
                pesoaccion=pesoaccion,
            )

class EventDescription(models.Model, ExcelImportMixin):

    """Extra table for text composition"""
    profile = models.ForeignKey(Profile)
    textoev2 = models.IntegerField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    text = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.text

    @classmethod
    def do_import_excel(cls, workbook, models):
        # models.profile.eventdescription_set.create()
        fields = ('idtextoev2', 'value', 'textoev2')
        for idtextoev2, value, textoev2 in workbook.iter_as_dict('textoevtipo', fields):
            models.profile.eventdescription_set.create(
                textoev2=idtextoev2,
                value=value or None,
                text=textoev2
            )

    class Meta:
        verbose_name = _('Event Description')
        verbose_name = _('Event Descriptions')




class ComEventKind(models.Model, ExcelImportMixin):
    '''Gives a type to communication event'''
    code = models.IntegerField()
    texto_2 = models.IntegerField()
    pesoaccion = models.IntegerField()

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = 'com'
        ordering = ('code',)
        verbose_name = _("Communication Event Kind")
        verbose_name = _("Communication Event Kinds")

    @classmethod
    def do_import_excel(cls, workbook, models):
        pass

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
            return EventText.objects.get(idtextoev2=self.kind.texto_2)

    class Meta:
        db_table = 'eventcom'
        verbose_name = _("Communication Event")
        verbose_name_plural = _("Communication Events")


class AI(MV, ExcelImportMixin):

    '''
    Analog Input
    '''
    WATCHED_FIELDS = ('value',)

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

    nroai = models.IntegerField(default=0)
    idtextoevm = models.IntegerField(null=True, blank=True)

    value_max = models.IntegerField(null=True, blank=True)
    value_min = models.IntegerField(null=True, blank=True)
    delta_h = models.IntegerField(null=True, blank=True)
    delta_l = models.IntegerField(null=True, blank=True)
    idtextoev2 = models.IntegerField(null=True, blank=True)
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

    @classmethod
    @counted
    def do_import_excel(cls, workbook, models):
        """Import AI for IED from 'ai' sheet"""

        def ai_belongs_to_ied(row):
            try:
                if int(row.ied_id) != models.ied.pk:
                    return False
            except ValueError:
                return False
            return True
        fields = (
                  'id',
                  'ied_id',  # Taken as IED offset
                  'offset',
                  'channel',
                  'trasducer',
                  'description',
                  'tag',
                  'unit',
                  'multip_asm',
                  'divider',
                  'reltv',
                  'relti',
                  'rel33_13',
                  'escala',
                  'q',
                  'value',
                  'nroai',
                  'valuemax', 'valuemin',
                  'idtextoevm',
                  'deltah', 'deltal',
                  'idtextoev2',
                  'pesoaccionh', 'pesoaccionl'
                  )


        for n, (pk, ied_id, offset, channel, trasducer,
                description, tag, unit, multip_asm, divider,
                rel_tv, rel_ti, rel_33_13, escala, q, value,
                nroai, value_max, value_min, idtextoevm,
                delta_h, delta_l, idtextoev2, pesoaccion_h, pesoaccion_l
                )\
            in enumerate(workbook.iter_as_dict('ai',
                                               fields=fields,
                                               row_filter=ai_belongs_to_ied)):
            try:
                pk = int(pk)
                if ied_id != models.ied.pk:
                    raise ValueError("Not related row")
            except ValueError as e:
                print e

            models.ied.ai_set.create(
                pk=pk,
                offset=offset,
                channel=channel,
                trasducer=trasducer,
                description=description,
                tag=tag,
                unit=unit,
                multip_asm=multip_asm,
                divider=divider,
                rel_tv=rel_tv,
                rel_ti=rel_ti,
                rel_33_13=rel_33_13,
                escala=escala,
                q=q,
                value=value,
                nroai=nroai,
                value_max=value_max or None, value_min=value_min or None,
                idtextoevm=idtextoevm,
                delta_h=delta_h or None, delta_l=delta_l or None,
                idtextoev2=idtextoev2,
                pesoaccion_h=pesoaccion_h or None, pesoaccion_l=pesoaccion_l or None,
            )


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


class Action(models.Model, ExcelImportMixin):
    profile = models.ForeignKey(Profile)
    bit = models.IntegerField()
    description = models.CharField(max_length=50)
    script = models.CharField(max_length=50)
    arguments = models.CharField(max_length=50)

    @classmethod
    def get_actions_for_peso(cls, peso):
        bit_values = []
        for i in range(32):
            bit_val = 1 << i
            if peso & bit_val:
                bit_values.append(bit_val)
        return cls.objects.filter(bit__in=bit_values)

    def __unicode__(self):
        return self.description

    @classmethod
    def do_import_excel(cls, workbook, models):
        fields = ('idaccion', 'accion', 'direccion')
        for bit, description, arguments in workbook.iter_as_dict('accionev', fields):
            models.profile.action_set.create(
                bit=bit,
                description=description[:50],
                arguments=arguments[:50],
            )

    class Meta:
        unique_together = ('bit',)
        verbose_name = _("Action")
        verbose_name_plural = _("Actions")

