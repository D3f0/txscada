# encoding: utf-8
from datetime import datetime
from json import dumps
import logging
import re

import adminactions.actions as actions
from nguru.apps.hmi.forms import (
    SVGElementForm,
    FormuluaInlineForm,
    SVGScreenAdminForm,
    UserForm,
    GroupForm,
)
from nguru.apps.hmi.models import (
    SVGScreen,
    Color,
    SVGPropertyChangeSet,
    Formula,
    SVGElement,
    UserProfile,
)

from nguru.apps.notifications.models import (
    SMSNotificationAssociation,
    EmailNotificationAssociation,
    NotificationRequest,
)

from constance.admin import Config, ConstanceAdmin
from django.conf import settings
from django.conf.urls import url, patterns
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.forms.util import flatatt
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from mailer.models import Message, MessageLog

from nguru.apps.mara.models import (
    Profile,
    COMaster, IED, SV, DI, AI, Event, Energy,
    EventText, ComEvent, Action, ComEventKind,
    EventDescription,
)
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models


# register all adminactions
logger = logging.getLogger(__name__)

site = admin.AdminSite('mara')
actions.add_to_site(site)


class COMasterTabularInline(admin.TabularInline):
    model = COMaster
    extra = 0

class IEDInline(admin.TabularInline):
    model = IED
    fields = ('rs485_address', 'offset')

#=========================================================================================
# Administración de COMaster
#=========================================================================================


class COMasterAdmin(admin.ModelAdmin):
    list_display = ('ip_address',
                    'enabled',
                    'port',
                    'poll_interval',
                    'rs485_source',
                    'rs485_destination',
                    'sequence',
                    'peh_time',
                    'get_last_peh',
                    'description'
                    )

    fieldsets = (
         # (_("Internal"), {
         #   'classes': ('collapse', ),
         #   'fields': ('profile', )
         #   }),
        (None, {
            'fields': ('description', ),
         }),
        (_("Connection"),{
            'fields': ('enabled', ('ip_address', 'port'), )
            }),
        (_("Timming"), {
            'fields': (('poll_interval', 'peh_time',
                'max_retry_before_offline',
                'exponential_backoff',), )
            }),
        (_('Mara settings'), {
            'fields': (('rs485_source', 'rs485_destination', ),
                )
            }
            ),
        (_('Mara debug'), {
            'fields': ('custom_payload_enabled', 'custom_payload')
            })

    )

    list_display_links = ('ip_address',)
    list_filter = ('enabled', )

    def get_last_peh(self, obj):
        if obj.last_peh:
            return obj.last_peh.strftime('%Y/%m/%d %H:%M:%S')
        return ''
    get_last_peh.short_description = _("Last PEH")
    get_last_peh.admin_order_field = 'last_peh'

site.register(COMaster, COMasterAdmin)


class AITabularInline(admin.TabularInline):
    model = AI
    extra = 0


class DITabularInline(admin.TabularInline):
    model = DI
    extra = 0


class SVTabularInline(admin.TabularInline):
    model = SV
    extra = 0


class IEDAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'offset', 'rs485_address', 'co_master')
    list_filter = ('co_master', 'offset', 'rs485_address')

    inlines = [AITabularInline, DITabularInline, SVTabularInline]

site.register(IED, IEDAdmin)


class SVAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'ied', 'offset', 'get_value')
    list_filter = ('ied', 'offset', )
    list_search = ('description', )
    exclude = ('last_update', )

    def get_value(self, obj):
        return ("%.4x" % obj.value).upper()

    get_value.short_description = _('value')
    get_value.admin_order_field = 'value'

site.register(SV, SVAdmin)


class DIAdmin(admin.ModelAdmin):
    list_display = ('get_tag',
                    'description',
                    'port',
                    'bit',
                    'trasducer',
                    'value',
                    'q',
                    'trasducer',
                    'maskinv',
                    'get_tipo', )
    list_filter = ('ied', 'tipo', )
    search_fields = ('tag', 'description')

    def get_tag(self, di):
        tag = di.tag
        if not tag:
            tag = "Sin tag"
        return tag
    get_tag.short_description = "Tag"

    def get_tipo(self, obj):
        attrs = {
                    'class': 'generate_event',
                    'href': reverse('admin:create_event', args=(obj.pk,)),
                    'title': 'Haga click para generar enveto de prueba',
                    'data-dialog-title': 'Generar evento para %s' % obj.tag,
                    'data-dialog-description': obj.description,
                }
        return '<a %s>Tipo %s</a>' % (flatatt(attrs), obj.tipo)

    get_tipo.allow_tags = True
    get_tipo.admin_order_field = 'tipo'
    get_tipo.short_description = 'tipo'

    class Media:
        css = {
            "all": (
                'js/jquery-ui-1.10.0.custom/development-bundle/themes/base/jquery-ui.css',
            )
        }
        js = (
            'initializr/js/vendor/jquery-1.9.0.min.js',
            'js/jquery-ui-1.10.0.custom/development-bundle/ui/jquery-ui.custom.js',
            'hmi/js/admin_di.js',
        )

    def get_urls(self):
        urls = patterns('',
            url(r'^create_event/(?P<di_pk>\d+)/$',
                self.admin_site.admin_view(self.create_event_view),
                name="create_event"),
        )
        return urls + admin.ModelAdmin.get_urls(self)

    def create_event_view(self, request, di_pk):
        '''
        Creates an evento for simulation (called from admin_di.js on tipo column)
        '''
        di = get_object_or_404(self.model, pk=di_pk)
        try:
            value = int(request.REQUEST.get('value', 0))
        except ValueError:
            response = HttpResponse("Valor no permitido: %s" % value, status=503)

        timestamp = datetime.now()
        created_event = di.events.create(timestamp=timestamp,
                                         value=value, q=0)
        resp = '''
            Se creó el evento <b>{created_event}</b> con ID={pk} y value={value}
        '''.format(created_event=created_event,
                   pk=created_event.pk,
                   value=value)
        return HttpResponse(resp)


site.register(DI, DIAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ('tag', '__unicode__', 'bit', 'port', 'value',
                    'get_timestamp', 'get_timestamp_ack', 'operations',
                    'username',)

    ordering = ('-timestamp', )
    list_filter = ('timestamp', 'timestamp_ack', 'username')

    def get_timestamp(self, obj):
        if obj.timestamp:
            return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
    get_timestamp.short_description = "Estampa temporal"
    get_timestamp.admin_order_field = 'timestamp'

    def get_timestamp_ack(self, obj):
        if obj.timestamp:
            return obj.timestamp_ack.strftime('%Y-%m-%d %H:%M:%S.%f')
    get_timestamp_ack.short_description = u"Estampa temporal atención"
    get_timestamp_ack.admin_order_field = 'timestamp_ack'

    def operations(self, obj):
        if not obj.timestamp_ack:
            return '<a class="attend" href="#">%s</a>' % (_('Attend'))
        else:
            return '&nbsp;'

    operations.allow_tags = True
    operations.short_description = _('actions')

    def tag(self, event):
        tag = event.di.tag
        if not tag:
            tag = "Sin Tag"
        return tag

    def bit(self, event):
        return event.di.bit

    def port(self, event):
        return event.di.port

    class Media:
        js = ('hmi/js/event_admin.js', )


site.register(Event, EventAdmin)


class EventDescriptionAdmin(admin.ModelAdmin):
    list_display = ('textoev2', 'value', 'text')
    list_display_links = ('text', )

site.register(EventDescription, EventDescriptionAdmin)


class AIAdmin(admin.ModelAdmin):
    list_display = ('tag', 'description', 'unit', 'channel',
                    'ied', 'offset', 'value', 'human_value', 'hex')
    list_filter = ('ied',)
    search_fields = ('tag', 'description')

    def hex(self, object):
        return ("%.4x" % object.value).upper()


site.register(AI, AIAdmin)


class EnergyAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'ai', 'value', 'q', 'hnn', 'code')
    list_filter = ('timestamp', 'ai', 'hnn', 'q')
site.register(Energy, EnergyAdmin)


class EventTextAdmin(admin.ModelAdmin):
    list_display = ('description', 'value', 'idtextoev2')

site.register(EventText, EventTextAdmin)


class SVGScreenAdmin(admin.ModelAdmin):
    list_display = ['get_hierachy', 'description', 'parent', 'show_svg', ]

    def show_svg(self, model):
        return u'<a href="{}" target="_blank">Download {}</a>'.format(
            model.svg.url,
            model.name
            )
    show_svg.allow_tags = True
    show_svg.short_description = _("Download")

    def get_hierachy(self, obj):
        hierachy = [ obj,]
        while obj.parent:
            obj = obj.parent
            hierachy.insert(0, obj)
        print hierachy
        return '->'.join([ x.name for x in hierachy])


    get_hierachy.short_description = _('label')

    def get_tags(self, obj):
        try:
            tags = obj.tags
        except IOError:
            tags = []
        count = len(tags)
        items = ''.join(['<li>%s</li>' % x[0] for x in tags.iteritems()])
        return '''
        <a class="show_tags" href="#">{count}</a>
        <span style="display: none;">
            <ul>{items}
            </ul>
        </span>
        '''.format(**locals())

    get_tags.allow_tags = True

    form = SVGScreenAdminForm

    class Media:
        css = {

            "all": (
            'js/jquery-ui-1.10.0.custom/development-bundle/themes/base/jquery-ui.css',
            "my_styles.css",)
        }
        js = (
            'initializr/js/vendor/jquery-1.9.0.min.js',
            'js/jquery-ui-1.10.0.custom/development-bundle/ui/jquery-ui.custom.js',
            'hmi/js/formula_admin_changelist.js',
            "hmi/js/admin_svgscreen.js",)

site.register(SVGScreen, SVGScreenAdmin)


class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'sample']

    def sample(self, color_instance):
        color = color_instance.color
        return '<span style="display: block; width: 15px; height: 15px; background: %s"></span>' % color

    sample.allow_tags = True

site.register(Color, ColorAdmin)


class SVGPropertyChangeSetAdmin(admin.ModelAdmin):
    list_display = ('index', 'description', 'color', )

    def get_example(self, svgprop):
        css = {}
        if svgprop.fill:
            css['background-color'] = svgprop.fill.color
        if svgprop.stroke:
            css['border-color'] = svgprop.stroke.color
        style = ';'.join(["%s: %s" % (k, v) for k, v in css.items()])
        return '<span style="{}">{}</span>'.format(style,
                                                   svgprop.description or 'example')

    get_example.allow_tags = True

site.register(SVGPropertyChangeSet, SVGPropertyChangeSetAdmin)


class ComEventKindAdmin(admin.ModelAdmin):
    list_display = ('code', 'texto_2', 'pesoaccion')

site.register(ComEventKind, ComEventKindAdmin)


class ComEventAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'comaster_desc',
                    'ied',
                    'timestamp',
                    'motiv',
                    'timestamp_ack',
                    'user')
    list_display_links = ('timestamp', )

    def comaster_desc(self, obj):
        return obj.ied.co_master.description or obj.ied.co_master.ip_address
    comaster_desc.short_description = "CO Master"

site.register(ComEvent, ComEventAdmin)


class FormulaAdmin(admin.ModelAdmin):

    list_display = ('get_screen',
                    'target',
                    'get_attribute',
                    'get_formula',
                    'last_error',
                    'get_calculate_link'
                    )

    search_fields = ('formula', )
    list_search = ('tag', )
    list_display_links = ('target', )
    list_filter = ('attribute', 'target__screen', )

    def get_screen(self, obj):
        return obj.target.screen
    get_screen.short_description = _('screen')
    get_screen.allow_tags = True
    get_screen.admin_order_field = 'target__screen'

    FORMULA_TEXT = dict(Formula.ATTRIBUTE_CHOICES)

    def get_attribute(self, obj):
        return FormulaAdmin.FORMULA_TEXT.get(obj.attribute, _("Invalid"))
    get_attribute.short_description = _('attribute')
    get_attribute.admin_order_field = 'attribute'

    def get_calculate_link(self, obj):
        '''Debug function'''
        html = '<a {attrs} href="{link}">{text}</a>'
        data = {
                    'title': 'Calculate %s' % obj,
                    'formula': obj.formula,
                }
        html = html.format(link='#',
                           text=_("Calculate"),
                           attrs=flatatt({
                                         'class': 'do_calculate',
                                         'data': dumps(data)
                                         })
                           )
        return html

    get_calculate_link.short_description = _('Calculate')
    get_calculate_link.allow_tags = True

    def get_formula(self, obj):
        '''Renders formula with JS hints'''
        formula = obj.formula
        try:

            def replace(match):
                tag = match.group('tag')
                input_type = match.group('input_type')
                link_text = '%s.%s' % (input_type, tag)
                fmt = u'''<a href="javascript:return void(0);"
                            title="{title}">{link_text}</a>'''

                return fmt.format(
                    title=obj.screen.profile.tag_description(tag, "Sin tag"),
                    link_text=link_text)

            formula = re.sub(u'(?P<input_type>\w{2})\.(?P<tag>[\w\d]+)',
                             replace,
                             formula,
                             re.UNICODE)

            return formula

        except Exception, e:
            logger.info("Exception %s in %s" % (e, formula))
            from traceback import format_exc
            logger.info(format_exc())
            return formula

    get_formula.short_description = 'Formula'
    get_formula.allow_tags = True

    class Media:
        js = ('initializr/js/vendor/jquery-1.9.0.min.js',
              'js/jquery-ui-1.10.0.custom/development-bundle/ui/jquery-ui.custom.js',
              'hmi/js/formula_admin_changelist.js', )
        css = {
            'all': ('js/jquery-ui-1.10.0.custom/development-bundle/themes/base/jquery-ui.css',)}

site.register(Formula, FormulaAdmin)


class FormulaTabularInline(admin.TabularInline):
    model = Formula
    form = FormuluaInlineForm

class SVGElementAdmin(admin.ModelAdmin):
    search_fields = ('tag', )
    list_display = ('tag', 'description', 'text', 'fill', 'stroke', 'get_mark',
                    'enabled', 'get_last_update', 'screen')

    list_filter = ('screen', 'mark', )
    inlines = [
        FormulaTabularInline,
    ]

    fieldsets = (
        (None, {'fields': ('screen', )}),
        (_('General information'), {'fields': (('tag', 'enabled'), 'description',)}),
        (_('Graphical attributes'), {'fields': (('fill', 'stroke', 'text', ), )}),
        (_('Interaction'), {
            'fields':
                ('on_click_jump', 'on_click_text_toggle', 'mark', 'linked_text_change'),
            'classes':
                ('collapse', ),
            }
        ),

    )


    def get_mark(self, obj):
        if obj.mark is not None:
            return obj.mark
        return "(Nada)"
    get_mark.short_description = "Mark"
    get_mark.admin_order_field = 'mark'

    def get_fill(self, obj):
        return u'''
        <?xml version="1.0" encoding="iso-8859-1"?>
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20001102//EN"
         "http://www.w3.org/TR/2000/CR-SVG-20001102/DTD/svg-20001102.dtd">

        <svg width="100%" height="100%">
          <g transform="">
            <rect x="0" y="0" width="150" height="50" style="{style}" />
            <text x="0" y="10" font-family="Verdana" font-size="12" fill="blue"
            style="dominant-baseline: -central;" >
                {desc}
            </text>
          </g>

        </svg>

        '''.format(style=obj.svg_style(), desc=str(obj.fill))

    get_fill.allow_tags = True
    get_fill.short_description = _("fill")

    def get_last_update(self, obj):
        retval = _('None')
        if obj.last_update:
            retval = obj.last_update.strftime(settings.TIMESTAMP_FORMAT)
        return retval
    get_last_update.short_description = _("last update")
    get_last_update.admin_order_field = 'last_update'

    form = SVGElementForm


site.register(SVGElement, SVGElementAdmin)


class ActionAdmin(admin.ModelAdmin):
    list_display = ('bit', 'description', 'script', 'arguments')
    list_display_links = ('description', )

site.register(Action, ActionAdmin)

# Config

site.register(Profile)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False


class UserAdmin(admin.ModelAdmin):
    model = User
    inlines = [UserProfileInline]
    form = UserForm
    list_display = ('username', 'get_name', 'is_active',
                    'last_login', 'email', 'is_staff', 'get_groups',
                    'get_cellphone')

    def get_name(self, obj):
        if not obj.last_name and not obj.first_name:
            return ''
        return ', '.join((obj.last_name or '', obj.first_name or ''))

    get_name.short_description = _('name').title()
    get_name.admin_order_field = 'last_name'


    def get_groups(self, obj):
        groups = [u'%s' % g for g in obj.groups.all()]
        if groups:
            retval = ', '.join(groups)
        else:
            retval = _('None')
        return retval

    get_groups.short_description = _("profile")
    get_groups.allow_tags = True

    def get_cellphone(self, obj):
        try:
            return obj.get_profile().cellphone or "--"
        except Exception:
            return "--"
    get_cellphone.short_description = "Número Celular"
    get_cellphone.allow_tags = True
    get_cellphone.admin_order_field = 'userprofile__cellphone'

    ## Static overriding
    fieldsets = (
        (None, {'fields': ('username', 'pass_1', 'pass_2')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

site.register(User, UserAdmin)


class GroupAdmin(admin.ModelAdmin):
    form = GroupForm

site.register(Group, GroupAdmin)
#site.register(Permission)


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('change_message', 'user', 'content_type', 'action_time',
                    'get_object_link', )
    list_display_links = ('change_message', )
    list_filter = ('user', 'content_type', 'action_flag')

    def get_object_link(self, logentry):
        from django.core.urlresolvers import reverse
        #import ipdb; ipdb.set_trace()
        view = 'mara:%s_%s_change' % (logentry.content_type.app_label,
                                      logentry.content_type.model)
        url = reverse(view, args=(logentry.object_id, ))
        return '''
        <a href="%s" target="_blank">%s</a>
        ''' % (url, 'Ver')
    get_object_link.allow_tags = True
    get_object_link.short_description = "Enlace"

site.register(LogEntry, LogEntryAdmin)

# Mail contol

def make_active(modeladmin, request, queryset):
    queryset.update(priority='2')

make_active.short_description = _('Put in queue')

class MessageAdmin(admin.ModelAdmin):
    actions = [make_active, ]
    list_display = ('to_address', 'priority', 'subject', 'when_added', )


site.register(Message, MessageAdmin)

class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('when_added', 'when_attempted', 'to_address', 'when_attempted', 'result', )
    list_filter = ('result', 'when_added')

# =======================================================================================
# Notifications
# =======================================================================================


class SMSNotificationAssociationAdmin(admin.ModelAdmin):
    model = SMSNotificationAssociation

    filter_horizontal = (
        'targets',
        'source_di',
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "targets":
            logger.info(db_field.name)
            lookup = dict(userprofile__cellphone__isnull=False)
            qs = User.objects.filter(**lookup)
            logger.debug("Modifying User queryset to %d", qs.count())
            kwargs["queryset"] = qs

        return super(SMSNotificationAssociationAdmin, self).formfield_for_dbfield(
            db_field,
            **kwargs
        )

site.register(SMSNotificationAssociation, SMSNotificationAssociationAdmin)

class EmailNotificationAssociationAdmin(admin.ModelAdmin):
    model = EmailNotificationAssociation

    filter_horizontal = ('targets', 'source_di', )

    list_display = ('name', 'get_targets', 'get_source_di', )


    def get_targets(self, obj):
        return ','.join(obj.targets.values_list('email', flat=True))

    get_targets.short_description = "Direcciones"

    def get_source_di(self, obj):
        from itertools import chain
        try:
            dis = obj.source_di.all()
            if dis.count() > 5:
                dis = dis[:5]
                tail = '...'
            else:
                tail = ''
            return ','.join(chain(map(unicode, dis.values_list('tag', flat=True)), [tail, ]))
        except Exception as e:
            return unicode(e)

    get_source_di.short_description = "DIs"

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "targets":
            logger.info(db_field.name)
            lookup = dict(email__icontains='@')
            qs = User.objects.filter(**lookup)
            logger.debug("Modifying User queryset to %d", qs.count())
            kwargs["queryset"] = qs

        return super(EmailNotificationAssociationAdmin, self).formfield_for_dbfield(
            db_field,
            **kwargs
        )



site.register(EmailNotificationAssociation, EmailNotificationAssociationAdmin)


class NotificationRequestAdmin(admin.ModelAdmin):
    model = NotificationRequest
    list_display = (
        'pk',
        'destination',
        'body',
        'status',
        'creation_time',
        'last_status_change_time',
        'get_source_di',
    )
    list_filter = ('destination', 'status', 'creation_time', 'last_status_change_time',)

    def get_source_di(self, notification):
        try:
            return '<a target="_target" href="{url}">{tag}</a>'.format(
                tag=notification.source.di.tag,
                url=reverse('admin:mara_di_change', args=(notification.source.di.pk,)),
            )

        except Exception, e:
            return unicode(e)

    get_source_di.short_description = "Tag origen"
    get_source_di.allow_tags = True
    # Not possible
    # get_source_di.admin_order_field = 'source__di__tag'

site.register(NotificationRequest, NotificationRequestAdmin)

site.register(MessageLog, MessageLogAdmin)
site.register([Config], ConstanceAdmin)
