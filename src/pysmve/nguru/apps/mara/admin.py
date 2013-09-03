# encoding: utf-8
import re
import logging
from django.contrib import admin

from models import (COMaster, IED, Unit, SV, DI, AI, Event, Energy,
                    ComEventKind, ComEvent, EventKind, Action)
from apps.hmi.models import SVGScreen, Color, SVGPropertyChangeSet, Formula, SVGElement

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
                    'rs485_source', 'rs485_destination','peh_time')
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

site.register(Unit)


class SVAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'value', 'ied', 'offset', 'value')
    list_filter = ('ied',)
    exclude = ('last_update', )

site.register(SV, SVAdmin)


class DIAdmin(admin.ModelAdmin):
    list_display = ('get_tag', 'description', 'port', 'bit', 'trasducer', 'value',  'ied')
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
    list_display = ('tag', '__unicode__', 'bit', 'port', 'value', 'timestamp', 'timestamp_ack')

    def tag(self, event):
        tag = event.di.tag
        if not tag:
            tag = "Sin Tag"
        return tag

    def bit(self, event):
        return event.di.bit

    def port(self, event):
        return event.di.port
site.register(Event, EventAdmin)


class AIAdmin(admin.ModelAdmin):
    list_display = ('tag', 'description', 'unit', 'channel', 'ied', 'offset', 'value', 'human_value', 'hex')
    list_filter = ('ied',)
    search_fields = ('tag', 'description')

    def hex(self, object):
        return ("%.4x" % object.value).upper()


site.register(AI, AIAdmin)
class EnergyAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'ai', 'value', 'q', 'hnn', 'code')
    list_filter = ('timestamp', 'ai', 'hnn', 'q')
site.register(Energy, EnergyAdmin)

site.register(EventKind)

class SVGScreenAdmin(admin.ModelAdmin):
    list_display = ['name', 'show_svg']

    def show_svg(self, model):
        return '<a href="#">Show {}</a>'.format(model)
    show_svg.allow_tags = True


    class Media:
        css = {
            "all": ("my_styles.css",)
        }
        js = ("hmi/js/admin_svgscreen.js",)

site.register(SVGScreen, SVGScreenAdmin)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'sample']

    def sample(self, color_instance):
        color = color_instance.color
        return '<span style="display: block; width: 15px; height: 15px; background: %s"></span>' % color

    sample.allow_tags = True

site.register(Color, ColorAdmin)

class SVGPropertyChangeSetAdmin(admin.ModelAdmin):
    list_display = ('description', 'index', 'example', 'background', 'foreground', )

    def example(self, svgprop):
        css = {}
        if svgprop.background:
            css['background-color'] = svgprop.background.color
        if svgprop.foreground:
            css['color'] = svgprop.foreground.color
        style = ';'.join(["%s: %s" % (k, v) for k, v in css.items()])
        return '<span style="{}">{}</span>'.format(style, svgprop.description or 'example')

    example.allow_tags = True

site.register(SVGPropertyChangeSet, SVGPropertyChangeSetAdmin)

class ComEventKindAdmin(admin.ModelAdmin):
    list_display = ('code', 'texto_2', 'pesoaccion')

site.register(ComEventKind, ComEventKindAdmin)

class ComEventAdmin(admin.ModelAdmin):
    list_display = ('ied', 'description', 'motiv', 'timestamp', 'timestamp_ack', 'user')
    list_display_links = ('description', )
site.register(ComEvent, ComEventAdmin)

class FormulaAdmin(admin.ModelAdmin):

    list_display = ('target', 'get_related_tag', 'attribute', 'get_formula',)
    list_search = ('tag', )
    list_fliter = ('attribute', )

    def get_related_tag(self, obj):
        s = '''<a class="svg_popup"
                  href="#"
                  tag="{tag}">
                  Ver</a>'''
        return s.format(tag=obj.tag)

    get_related_tag.short_description = 'SVG'
    get_related_tag.allow_tags = True


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


                return fmt.format(title=obj.screen.profile.tag_description(tag, "Sin tag"),
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
        css = {'all': ('js/jquery-ui-1.10.0.custom/development-bundle/themes/base/jquery-ui.css',)}

site.register(Formula, FormulaAdmin)

class SVGElementAdmin(admin.ModelAdmin):
    search_fields = ('tag', )
    list_display = ('tag', 'description', 'text', 'background', 'mark',
            'enabled', 'last_update')

site.register(SVGElement, SVGElementAdmin)

class ActionAdmin(admin.ModelAdmin):
    list_display = ('bit', 'descripcion', 'script', 'argumentos')

site.register(Action, ActionAdmin)
