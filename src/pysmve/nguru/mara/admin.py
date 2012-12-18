from django.contrib import admin

from models import Profile, COMaster, IED, Unit, SV, DI, AI, Event, EnergyPoint, Energy

site = admin.AdminSite('mara')

site.register(Profile)
class COMasterAdmin(admin.ModelAdmin):
    list_display = ('profile', 'ip_address', 'enabled', 'port', 'poll_interval',
                    'rs485_source', 'rs485_destination',)
    list_display_links = ('ip_address',)

site.register(COMaster, COMasterAdmin)

class IEDAdmin(admin.ModelAdmin):
    list_display = ('co_master', 'offset', 'rs485_address')
    list_filter = ('co_master',)

site.register(IED, IEDAdmin)

site.register(Unit)

class SVAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'unit', 'width', 'value', 'ied',)
    list_filter = ('ied',)

site.register(SV, SVAdmin)

class DIAdmin(admin.ModelAdmin):
    list_display = ('param', 'port', 'bit', 'description', 'ied')
    list_filter = ('ied',)
    #list_display_links = ()


site.register(DI, DIAdmin)
site.register(Event)

class AIAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'unit', 'description', 'ied')
    list_filter = ('ied',)

site.register(AI, AIAdmin)

site.register(Energy)

class EnergyPointAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'channel', 'description', 'offset', 'param',
                    'ke', 'divider', 'rel_tv', 'rel_ti', 'rel_33_13', 'ied',)
    list_filter = ('ied', 'channel',)
site.register(EnergyPoint, EnergyPointAdmin)
