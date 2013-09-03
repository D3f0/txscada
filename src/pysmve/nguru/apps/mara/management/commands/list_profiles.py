from django.core.management.base import NoArgsCommand

def comaster_ips(profile):
    for co_master in profile.comasters.all():
        yield '%s:%d' % (co_master.ip_address, co_master.port)

class Command(NoArgsCommand):
	help = "List profiles"

	def handle_noargs(self, **options):
		from apps.mara.models import Profile
		for profile in Profile.objects.all():
			print "[%s] %s" % ("*" if profile.default else ' ', profile.name, ),\
                    ', '.join(comaster_ips(profile))