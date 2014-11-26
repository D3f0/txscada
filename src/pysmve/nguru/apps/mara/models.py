# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import logging
import operator
import re  # For text frame procsessing

from constance import config
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import models
from django.db.models import signals
from django.template import Template, Context
from django.utils.translation import ugettext as _
from protocols import constants
from protocols.constructs.structs import container_to_datetime
from protocols.utils.bitfield import iterbits
from utils import ExcelImportMixin, counted, import_class, get_setting
from timedelta.fields import TimedeltaField


# Dettached email handler
if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail


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
        if self.pk not in Profile._tag_info:
            Profile._tag_info[self.pk] = self.load_tags()
        return Profile._tag_info[self.pk].get(tag, empty_text)

    __tags = None

    @property
    def tags(self):
        if not self.__tags:
            self.__tags = self.load_tags()
        return self.__tags

    @classmethod
    def get_by_name(cls, name):
        '''Get the profile'''
        if name is None:
            return Profile.objects.get(default=True)
        else:
            try:
                return Profile.objects.get(name__iexact=name)
            except Profile.DoesNotExist:
                return None

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
    # ------------------------------------------------------------------------
    # Timing values
    # ------------------------------------------------------------------------
    poll_interval = models.FloatField(
        verbose_name="Poll interval in seconds",
        default=5
    )
    exponential_backoff = models.BooleanField(default=False,
                                              help_text="Make queries")

    max_retry_before_offline = models.IntegerField(default=3)

    sequence = models.IntegerField(help_text=u"Current sequence number",
                                   default=0)

    rs485_source = models.SmallIntegerField(
        default=64,
        help_text='RS485 source address'
    )
    rs485_destination = models.SmallIntegerField(
        default=1,
        help_text='Mara protocol DEST field in poll'
    )

    process_pid = models.IntegerField(blank=True, null=True,
                                      default=None,
                                      editable=False,
                                      help_text="PID del proceso que se encuentra utiliza"
                                      "ndo el proceso")

    peh_time = TimedeltaField(
        default=timedelta(hours=1),
        verbose_name=_("PEH Interval"),
        help_text="Tiempo entre puesta en hora",
    )

    last_peh = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Last PEH sent to this COMaster"),
    )

    custom_payload = models.TextField(null=True,
                                      blank=True,
                                      help_text=_('Custom payload without SOF SEQ SRC DST'
                                                  '// CRH CRL'))

    custom_payload_enabled = models.BooleanField(default=False)

    description = models.CharField(max_length=100,
                                   null=True,
                                   blank=True)

    def needs_peh(self):
        '''Checks if last peh was made'''

        should_sync = False
        if self.last_peh is None:
            should_sync = True
        else:
            delta = (datetime.now() - self.last_peh)
            if abs(delta) > self.peh_time:
                should_sync = True
        return should_sync

    def update_last_peh(self, timestamp):
        '''Updates last PEH timestamp in database'''
        # On newer django versions, save could specify exaclty which field
        self.last_peh = timestamp
        return self.save()

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
        permissions = (
            ('can_insert_frame_manually', _('Can insert frames manually')),
        )

    def process_frame(self, mara_frame,
                      update_states=True,
                      update_di=True,
                      update_ai=True,
                      update_sv=True,
                      create_events=True,
                      create_ev_digital=True,
                      create_ev_energy=True,
                      create_ev_comsys=True,
                      calculate=True,
                      logger=None):
        '''Takes a Mara frame (from construct) and saves its components
        in related COMaster models (DI, AI, SV) and Events.
        It accepts flags for processing. There are two general flags called
        update_states and create_events, that when false disable processing
        of states and events acordingly.
        There are 3 fine grained flags for states and 3 for event types'''
        if not logger:
            logger = logging.getLogger('commands')

        # Flags for states
        update_di = update_di and update_states
        update_ai = update_ai and update_states
        update_sv = update_sv and update_states
        # Flags for events
        create_ev_digital = create_ev_digital and create_events
        create_ev_energy = create_ev_energy and create_events
        create_ev_comsys = create_ev_comsys and create_events

        try:
            payload = mara_frame.payload_10
        except AttributeError as e:
            raise AttributeError(
                "Mara payload not present. %s does not look like a frame" %
                mara_frame
            )
        # Some counters
        di_count, ai_count, sv_count, event_count = 0, 0, 0, 0
        timestamp = datetime.now()

        if update_di:
            for value, di in zip(iterbits(payload.dis, length=16), self.dis):
                # Update value takes care of maskinv
                di.update_value(value, q=0, last_update=timestamp)
                di_count += 1
        else:
            if len(payload.dis):
                logger.info("Skipping DI")

        if update_ai:
            for value, ai in zip(payload.ais, self.ais):
                value = value & 0x0FFF
                q = (value & 0xC000) >> 14
                ai.update_value(value, last_update=timestamp, q=q)
                ai_count += 1

        if update_sv:
            for value, sv in zip(payload.varsys, self.svs):
                sv.update_value(value, last_update=timestamp)
                sv_count += 1

        logger.info(_("Processing %s events") % len(payload.event))
        for event in payload.event:
            if event.evtype == 'DIGITAL' and create_ev_digital:
                # Los eventos digitales van con una DI
                try:
                    di = DI.objects.get(ied__rs485_address=event.addr485,
                                        ied__co_master=self,
                                        port=event.port,
                                        bit=event.bit)
                    ev = di.events.create(
                        timestamp=container_to_datetime(event),
                        q=event.q,
                        value=event.status ^ di.maskinv
                    )
                    logger.info(_("Digital event created %s") % ev)
                except DI.DoesNotExist:
                    logger.warning(
                        "DI does not exist for %s:%s", event.port, event.bit)

            elif event.evtype == 'ENERGY' and create_ev_energy:
                try:
                    query = dict(
                        ied__rs485_address=event.addr485,
                        ied__co_master=self,
                        channel=event.channel,
                    )
                    ai = AI.objects.get(**query)
                    timestamp = container_to_datetime(event)
                    # Parsing construct arrray bogus data
                    value = event.data[
                        1] + (event.data[0] << 8) + (event.data[2] << 16)
                    ev = ai.energy_set.create(
                        timestamp=timestamp,
                        code=event.code,
                        q=event.q,
                        hnn=event.hnn,
                        value=value
                    )
                    logger.info(_("Energy created: %s") % ev)
                except AI.DoesNotExist:
                    logger.warning(_("AI for energy does not exist"))
                except AI.MultipleObjectsReturned:
                    logger.warning(_("AI for energy has multiple matches"))
            elif event.evtype == 'COMSYS' and create_ev_comsys:
                try:
                    ied = self.ieds.get(rs485_address=event.addr485)
                    timestamp = container_to_datetime(event)
                    ev = ied.comevent_set.create(
                        motiv=event.motiv,
                        timestamp=timestamp
                    )
                    logger.info("ComEvent created: %s" % ev)
                except ComEvent.DoesNotExist:
                    logger.warning(_("Cannot create COMSYS event"))

        if calculate:
            from apps.hmi.models import Formula
            logger.info("Starting formula update")
            try:
                Formula.calculate()
                logger.info("Formula update OK")
            except Exception as e:
                logger.error(unicode(e), exc_info=True)

        return di_count, ai_count, sv_count, event_count

    def next_sequence(self):
        """
        Goes to the next sequence and save it.
        If using from twisted should be used with deferToThread.
        """
        if self.sequence < constants.sequence.MIN.value:
            self.sequence = constants.sequence.MIN.value
        else:
            self.sequence += 1
            if self.sequence > constants.sequence.MAX.value:
                self.sequence = constants.sequence.MIN.value
        self.save()
        return self.sequence

    def _process_str_frame(self, a_text_frame, **flags):
        '''
        Creates crecords from frame into a COMaster entity tree.
        This **should** not be used in poll function. It's a helper for
        commandline for easy recovery of not saved frames.
        Accepts a frame per line.
        @return True on success, False otherwise
        '''
        from protocols.constructs.structs import hexstr2buffer
        from protocols.constructs import MaraFrame

        buff = hexstr2buffer(a_text_frame)
        frame = MaraFrame.parse(buff)
        success = True
        try:
            self.process_frame(frame)
        except Exception:
            success = False
        return success

    _frame_regex = re.compile(r'(FE ([0-9A-F]{2}\s?){2,512})', re.IGNORECASE)

    def _process_text_frames(self, text, **flags):
        '''Process many frames. Looks insde text, and can accept file object.
        @returns (frames_found, frames_processed)'''
        if hasattr(text, 'read'):
            text = text.read()
        found, processed = 0, 0
        for line in text.split('\n'):
            match = self._frame_regex.search(line)
            if match:
                found += 1
                text_frame = match.group()

                self._process_str_frame(text_frame, **flags)
                processed += 1

        return found, processed

    def _process_frame_file(self, path, **flags):
        with open(path) as fp:
            ok, n = 0, 0
            for n, line in enumerate(fp.readlines()):
                if not line:
                    continue
                match = self._frame_regex.search(line)
                if match:
                    text_frame = match.group()
                    if self._process_str_frame(text_frame, **flags):
                        ok += 1
                # print tr.print_diff()

        return n, ok

    def set_ai_qualifier(self, value, last_update=None):
        '''Propagates q for all AI belonging to an COMaster (through IED)'''
        if not last_update:
            last_update = datetime.now()
        return self.ais.update(q=value, last_update=last_update)

    @classmethod
    def do_import_excel(cls, workbook, models, logger):
        """Import COMaster from excel sheet. This is the base import, does not any
        filtering."""
        fields = ('id', 'ip_address', 'port', 'enabled')
        dataiter = workbook.iter_as_dict('comaster', fields=fields)
        for i, (pk, ip_address, port, enabled) in enumerate(dataiter):

            enabled = bool(int(enabled))
            # TODO: Make imports work

            comaster = models.profile.comasters.create(id=pk,
                                                       ip_address=ip_address,
                                                       port=port,
                                                       enabled=enabled,
                                                       )
            IED.import_excel(
                workbook, profile=models.profile, comaster=comaster)

    def get_protocol_factory(self):
        '''Creates the instance of the protocol factory for a given COMaster'''

        prtocol_factory = get_setting('POLL_PROTOCOL_FACTORY',
                                      'protocols.mara.client.MaraClientProtocolFactory')
        pf_class = import_class(prtocol_factory)

        instance = pf_class(self)
        return instance


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
    def do_import_excel(cls, workbook, models, logger):
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

    @classmethod
    def do_import_excel(cls, workbook, models, logger):
        """Import SV (System Variables) from excel sheet"""
        fields = "ied_id    offset  bit param   description value".split()
        # Determine call
        update = 'ieds' in models

        def sv_belongs_to_ied(row):
            try:
                if (row.ied_id) != models.ied.pk:
                    return False
            except ValueError:
                return False
            return True

        if not update:

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
        else:
            logger.info("Deleting")
            SV.objects.filter(ied__in=models.ieds).delete()
            # Update
            for ied in models.ieds:
                rows = workbook.iter_as_dict('varsys', fields=fields)
                logger.info(_("Importing IED: %s"), ied)
                for t in (row for row in rows if row.ied_id == ied.pk):
                    ied_id, offset, bit, param, description, value = t
                    try:
                        ied.sv_set.create(
                            offset=offset,
                            bit=bit,
                            param=param,
                            description=description,
                            value=value or 0
                        )
                    except IntegrityError as e:
                        logger.error(_("Error in %s"), e)


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
    TIPO_CHOICES = (
        (0, 'Tipo 0'),
        (1, 'Tipo 1'),
        (2, 'Tipo 2'),
    )
    tipo = models.IntegerField(default=0, choices=TIPO_CHOICES)

    def __unicode__(self):
        return u"DI %2d:%2d (%s)" % (self.port, self.bit, (self.tag or "Sin Tag"))

    class Meta:
        unique_together = ('offset', 'ied', 'port', 'bit')
        ordering = ('port', 'bit')
        verbose_name = _("Digital Input")
        verbose_name_plural = _("Digital Inputs")

    # DEBUG CODE. Likely to be removed
    # @classmethod
    # def check_value_change(cls, instance=None, **kwargs):
    #     try:
    #         if instance.pk:
    #             old_value = DI.objects.get(pk=instance.pk).value
    #             if old_value != instance.value:
    #                 print("%s change from %s -> %s at %s" % (instance,
    #                                                          old_value,
    #                                                          instance.value,
    #                                                          instance.last_update))
    #     except Exception as e:
    #         print(e)

    @classmethod
    def do_import_excel(cls, workbook, models, logger):
        """Import DI for IED from XLS di sheet"""

        fields = ('id',
                  'ied_id',
                  'offset',
                  'port',
                  'bit',
                  'tag',
                  'trasducer',
                  'description',
                  'q',
                  'value',
                  'maskinv',
                  'tipodi',
                  'nrodi',
                  'idtextoev2',
                  'pesoaccionh',
                  'pesoaccionl'
                  )
        for i, (
            pk, ied_id, offset, port, bit, tag, trasducer, description, q, value,
                maskinv, tipodi, nrodi, idtextoev2, pesoaccion_h, pesoaccion_l)\
            in enumerate(workbook.iter_as_dict('di',
                                               fields=fields)):

            ied = models.ieds.get(pk=ied_id)

            instance, created = ied.di_set.get_or_create(pk=pk)

            if created:
                action = "Created"
            else:
                action = "Updated"

            # Get related ied
            ied = models.ieds.get(pk=ied_id)

            instance.offset = offset
            instance.ied = ied
            instance.tag = tag
            instance.port = port
            instance.bit = bit
            instance.value = value
            instance.q = q
            instance.trasducer = trasducer
            instance.maskinv = maskinv
            instance.description = description
            instance.idtextoev2 = idtextoev2 or 0
            instance.pesoaccion_h = pesoaccion_h or 0
            instance.pesoaccion_l = pesoaccion_l or 0
            instance.save()
            logger.info("DI %s %s", instance, action)

    def update_value(self, value, **kwargs):
        value = value ^ self.maskinv
        return super(DI, self).update_value(value, **kwargs)

# signals.pre_save.connect(DI.check_value_change, sender=DI)


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
    show = models.BooleanField(default=True, help_text=_("Show in alarm grid"))
    username = models.CharField(max_length=100, blank=True, null=True,
                                help_text=_('User who attended the event.'
                                            'Typically through API call.'))

    # Keys are profiles, then textev2, value, then text
    _descriptions = {}

    def get_current_descriptions(self):
        '''Returns a dictionary of descriptions for current profile'''
        profile = self.di.ied.co_master.profile
        if profile.pk not in Event._descriptions:
            desc_dict = Event._descriptions.setdefault(profile.pk, {})
            fields = 'textoev2', 'value', 'text'
            value_list = profile.eventdescription_set.values_list(*fields)
            for textoev2, value, text in value_list:
                values_dict = desc_dict.setdefault(textoev2, {})
                values_dict[value] = text
        return Event._descriptions[profile.pk]

    @property
    def text2(self):
        try:
            text2 = self.get_current_descriptions()[
                self.di.idtextoev2][self.value]
        except Exception as e:
            text2 = unicode(e)
        return text2

    def __unicode__(self):
        return "%s %s" % (self.di.description or "No description", self.text2)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def propagate_changes(self):
        from apps.hmi.models import SVGElement
        # if self.di.tipo == 0:
        #     if self.value == 0:
        #         self.show = False
        # if self.di.tipo in [0, 1]:
        #
        #     text = '1' if self.timestamp_ack else '0'
        #     SVGElement.objects.filter(screen__profile=self.di.ied.co_master.profile,
        #                               tag=self.di.tag).update(text=text)
        lookup = {'screen__profile': self.di.ied.co_master.profile}
        tag_qs = SVGElement.objects.filter(**lookup)
        tipo = self.di.tipo
        tag = self.di.tag
        if not self.timestamp_ack:
            if tipo == 0:
                tag_tmp = tag.replace('51_', '52B')
                text = '1'
                if self.value:
                    tag_qs.filter(tag=tag).update(text=text)
                    tag_qs.filter(tag=tag_tmp).update(text=text)
                else:
                    self.show = False
        else:
            # Attend event
            if tipo == 0:
                tag_qs.filter(tag=tag).update(text='0')
            elif tipo == 1:
                return
            elif tipo == 2:
                value = int(tag_qs.get(tag=tag).text)
                if value:
                    tag_qs.filter(tag=tag).update(text='0')


def sync_event_with_svgelements(instance=None, **kwargs):
    if instance:
        instance.propagate_changes()

signals.pre_save.connect(sync_event_with_svgelements, sender=Event)

# FIXME: Remove this table


class EventText(models.Model, ExcelImportMixin):

    '''Abstracción de textoev2'''
    profile = models.ForeignKey(Profile, related_name='event_kinds')
    description = models.CharField(max_length=50, blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    idtextoev2 = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('idtextoev2', 'value')
        verbose_name = _("Event Text")
        verbose_name_plural = _("Event Texts")

    def __unicode__(self):
        return self.description

    @classmethod
    def do_import_excel(cls, workbook, models, logger):
        """Import text for events from XLS sheet 'com'"""
        fields = 'id    code    description idTextoEv2  pesoaccion'.lower(
        ).split()
        for t in workbook.iter_as_dict('com', fields=fields):
            pk, code, description, idtextoev2, pesoaccion = t
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
    def do_import_excel(cls, workbook, models, logger):
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
    def do_import_excel(cls, workbook, models, logger):
        pass


class ComEvent(GenericEvent):
    motiv = models.IntegerField()
    ied = models.ForeignKey(IED)

    @property
    def description(self):
        return self.kind.description

    def __unicode__(self):
        return "COMEV %s MOTIV:%s" % (self.ied, self.motiv)

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
    peso_p = models.FloatField(verbose_name="PesoP", default=1)
    q = models.IntegerField(db_column="q", default=0)
    value = models.SmallIntegerField(default=-1)

    escala = models.FloatField(help_text="Precalculo de multip_asm, divider, reltv, "
                               "relti y rel33-13", default=0)
    escala_e = models.FloatField(help_text="Escala para energía",
                                 default=0)

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
                  self.peso_p,
                  self.value
                  ]
        return "%.2f %s" % (reduce(operator.mul, values), self.unit)

    @classmethod
    @counted
    def do_import_excel(cls, workbook, models, logger):
        """Import AI for IED from 'ai' sheet."""

        fields = ('id',
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
                  'peso_p',
                  'escala',
                  'escala_e',
                  # 'q',
                  # 'value',
                  'nroai',
                  'valuemax', 'valuemin',
                  'idtextoevm',
                  'deltah', 'deltal',
                  'idtextoev2',
                  'pesoaccionh', 'pesoaccionl'
                  )

        for n, (pk, ied_id, offset, channel, trasducer,
                description, tag, unit, multip_asm, divider,
                rel_tv, rel_ti, peso_p, escala, escala_e,
                # q, value,
                nroai, value_max, value_min, idtextoevm,
                delta_h, delta_l, idtextoev2, pesoaccion_h, pesoaccion_l
                )\
            in enumerate(workbook.iter_as_dict('ai',
                                               fields=fields)):

            pk = int(pk)
            ied_id = int(ied_id)

            try:

                ied = models.ieds.get(pk=ied_id)
                instance, created = AI.objects.get_or_create(pk=pk, ied=ied)

            except IED.DoesNotExist:
                logger.error("AI related IED cound not be found: %d", ied_id)
                raise

            if created:
                instance.ied = ied

            instance.offset = offset
            instance.channel = channel
            instance.trasducer = trasducer
            instance.description = description
            instance.tag = tag
            instance.unit = unit
            instance.multip_asm = multip_asm
            instance.divider = divider
            instance.rel_tv = rel_tv
            instance.rel_ti = rel_ti
            instance.peso_p = peso_p or 1.0
            instance.escala = escala
            instance.escala_e = escala_e or 1.0
            # instance.q = q
            # instance.value = value
            instance.nroai = nroai
            instance.value_max = value_max or None
            instance.value_min = value_min or None
            instance.idtextoevm = idtextoevm
            instance.delta_h = delta_h or None
            instance.delta_l = delta_l or None
            instance.idtextoev2 = idtextoev2
            instance.pesoaccion_h = pesoaccion_h or None
            instance.pesoaccion_l = pesoaccion_l or None
            try:
                instance.save()
            except Exception as e:
                raise e
            logger.info(
                "AI %s %s", instance, 'created' if created else 'updated')


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
        # unique_together = ('ai', 'timestamp', 'value')
        permissions = (
            ('can_view_power_plot', _('Can view power plot')),
            ('can_see_month_report', _('Can see month report')),
        )


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
    def do_import_excel(cls, workbook, models, logger):
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


def send_emails(created, instance, **kwargs):

    from constance import context_processors
    extra_context = context_processors.config(request=None)

    def comma_sep_to_users(comma_sep_str):
        users = [
            u for u in map(lambda s: s.strip(), comma_sep_str.split(',')) if u]
        return [user for user in User.objects.filter(username__in=users)]

    if created:
        if isinstance(instance, Event):
            users = comma_sep_to_users(config.EVENT_0_EMAIL)
        elif isinstance(instance, ComEvent):
            users = comma_sep_to_users(config.EVENT_3_EMAIL)
        else:
            users = []
        template = Template(config.TEMPLATE_EMAIL)
        for user in users:

            context = Context({'event': instance, 'user': user})
            context.update(extra_context)

            message = template.render(context)
            send_mail(subject='Alerta SMVE',
                      message=message,
                      from_email=settings.SERVER_EMAIL,
                      recipient_list=[user.email])

signals.post_save.connect(send_emails, sender=Event)
signals.post_save.connect(send_emails, sender=ComEvent)
