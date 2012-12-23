from django.contrib import admin

from models import Profile, COMaster, IED, Unit, SV, DI, AI, Event, EnergyPoint, Energy

site = admin.AdminSite('mara')

class COMasterTabularInline(admin.TabularInline):
    model = COMaster
    extra = 0

class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    inlines = [COMasterTabularInline, ]

site.register(Profile, ProfileAdmin)

#=========================================================================================
# 
#=========================================================================================


class COMasterAdmin(admin.ModelAdmin):
    list_display = ('profile', 'ip_address', 'enabled', 'port', 'poll_interval',
                    'rs485_source', 'rs485_destination',)
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
    list_display = ('__unicode__', 'unit', 'width', 'value', 'ied', 'offset', 'value')
    list_filter = ('ied',)

site.register(SV, SVAdmin)

class DIAdmin(admin.ModelAdmin):
    list_display = ('param', 'port', 'bit', 'value', 'description', 'ied')
    list_filter = ('ied',)
    #list_display_links = ()


site.register(DI, DIAdmin)
site.register(Event)

class AIAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'unit', 'description', 'ied', 'offset', 'value',)
    list_filter = ('ied',)

site.register(AI, AIAdmin)

site.register(Energy)

class EnergyPointAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'channel', 'description', 'offset', 'param',
                    'ke', 'divider', 'rel_tv', 'rel_ti', 'rel_33_13', 'ied',)
    list_filter = ('ied', 'channel',)
site.register(EnergyPoint, EnergyPointAdmin)
