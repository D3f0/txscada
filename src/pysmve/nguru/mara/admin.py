from django.contrib import admin

from models import Profile, COMaster, IED, Unit, DI, AI, Event, Energy

site = admin.AdminSite('mara')

site.register(Profile)
class COMasterAdmin(admin.ModelAdmin):
    list_display = ('profile', 'ip_address', 'enabled', 'port', 'poll_interval',
                    'rs485_source', 'rs485_destination',)
    list_display_links = ('ip_address',)

site.register(COMaster, COMasterAdmin)

class IEDAdmin(admin.ModelAdmin):
    list_display = ('co_master', 'offset', 'rs485_address')

site.register(IED, IEDAdmin)

site.register(Unit)

class DIAdmin(admin.ModelAdmin):
    list_display = ('ied', 'port', 'bit',)
    #list_display_links = ()

site.register(DI, DIAdmin)
site.register(Event)
site.register(AI)
site.register(Energy)
