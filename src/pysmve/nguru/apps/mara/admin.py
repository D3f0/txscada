# encoding: utf-8

from django.contrib import admin

from models import COMaster, IED, Unit, SV, DI, AI, Event, EnergyPoint, Energy
from apps.hmi.models import SVGScreen


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
    list_display = ('param', 'port', 'bit', 'value', 'description', 'ied')
    list_filter = ('ied',)
    #list_display_links = ()


site.register(DI, DIAdmin)
site.register(Event)


class AIAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'unit', 'description', 'ied', 'offset', 'value', 'human_value', 'hex')
    list_filter = ('ied',)

    def hex(self, object):
        return ("%.4x" % object.value).upper()


site.register(AI, AIAdmin)

site.register(Energy)


class EnergyPointAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'channel', 'description', 'offset', 'param',
                    'ke', 'divider', 'rel_tv', 'rel_ti', 'rel_33_13', 'ied',)
    list_filter = ('ied', 'channel',)
site.register(EnergyPoint, EnergyPointAdmin)



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
