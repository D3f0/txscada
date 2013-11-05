# encoding: utf-8
import re
import logging
from django.contrib import admin
from django.conf import settings

from models import (
    Profile,
    COMaster, IED, SV, DI, AI, Event, Energy,
    EventText, ComEvent, Action, ComEventKind,
    EventDescription,
)
from apps.hmi.models import SVGScreen, Color, SVGPropertyChangeSet, Formula, SVGElement

from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)

site = admin.AdminSite('mara')


class COMasterTabularInline(admin.TabularInline):
    model = COMaster
    extra = 0


#=========================================================================================
# Administración de COMaster
#=========================================================================================


class COMasterAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'enabled', 'port', 'poll_interval',
                    'rs485_source', 'rs485_destination', 'peh_time')
    list_display_links = ('ip_address',)
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
    list_display = ('__unicode__', 'value', 'ied', 'offset', 'value')
    list_filter = ('ied',)
    exclude = ('last_update', )

site.register(SV, SVAdmin)


class DIAdmin(admin.ModelAdmin):
    list_display = ('get_tag', 'description', 'port', 'bit', 'trasducer', 'value', 'q',
                    'trasducer', 'maskinv')
    list_filter = ('ied',)
    search_fields = ('tag', 'description')

    def get_tag(self, di):
        tag = di.tag
        if not tag:
            tag = "Sin tag"
        return tag

    get_tag.short_description = "Tag"


site.register(DI, DIAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ('tag', '__unicode__', 'bit', 'port', 'value',
                    'get_timestamp', 'get_timestamp_ack', 'operations')

    def get_timestamp(self, obj):
        if obj.timestamp:
            return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')

    def get_timestamp_ack(self, obj):
        if obj.timestamp:
            return obj.timestamp_ack.strftime('%Y-%m-%d %H:%M:%S.%f')

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
    list_display = ['name', 'show_svg', 'get_tags', ]

    def show_svg(self, model):
        return '<a href="#">Show {}</a>'.format(model)
    show_svg.allow_tags = True

    def get_tags(self, obj):
        tags = obj.tags
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
    list_display = ('ied', 'description', 'motiv', 'timestamp', 'timestamp_ack', 'user')
    list_display_links = ('description', )
site.register(ComEvent, ComEventAdmin)


class FormulaAdmin(admin.ModelAdmin):

    list_display = ('get_screen',
                    'target',
                    'get_attribute',
                    'get_formula',
                    'last_error',
                    )

    list_search = ('tag', )
    list_display_links = ('target', )
    list_filter = ('attribute', 'target__screen', )

    def get_screen(self, obj):
        return obj.target.screen

    def get_attribute(self, obj):
        try:
            return obj.attribute
            pass
        except Exception, e:
            return e

    get_attribute.short_description = _('attribute')
    get_attribute.admin_order_field = 'attribute'

    get_screen.short_description = 'SVG'
    get_screen.allow_tags = True
    get_screen.admin_order_field = 'target__screen'

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


class SVGElementAdmin(admin.ModelAdmin):
    search_fields = ('tag', )
    list_display = ('tag', 'description', 'text', 'fill', 'stroke', 'get_mark',
                    'enabled', 'get_last_update', 'screen')

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

site.register(SVGElement, SVGElementAdmin)


class ActionAdmin(admin.ModelAdmin):
    list_display = ('bit', 'description', 'script', 'arguments')
    list_display_links = ('description', )

site.register(Action, ActionAdmin)


# Config

config_site = admin.AdminSite('config')
config_site.register(Profile)
