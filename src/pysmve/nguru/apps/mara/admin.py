# encoding: utf-8

from django.contrib import admin

from models import (COMaster, IED, Unit, SV, DI, AI, Event, Energy,
                    ComEventKind, ComEvent)
from apps.hmi.models import SVGScreen, Color, SVGPropertyChangeSet


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


    def get_tag(self, di):
        tag = di.tag
        if not tag:
            tag = "Sin tag"
        return tag

    get_tag.short_description = "Tag"


site.register(DI, DIAdmin)
class EventAdmin(admin.ModelAdmin):
    list_display = ('tag', 'bit', 'port', 'value', 'timestamp', 'timestamp_ack')

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

    def hex(self, object):
        return ("%.4x" % object.value).upper()


site.register(AI, AIAdmin)

site.register(Energy)


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
    list_display = ('description', 'code', 'texto_2', 'pesoaccion')

site.register(ComEventKind, ComEventKindAdmin)

class ComEventAdmin(admin.ModelAdmin):
    list_display = ('ied', 'description', 'motiv', 'timestamp', 'timestamp_ack', 'user')
    list_display_links = ('description', )
site.register(ComEvent, ComEventAdmin)