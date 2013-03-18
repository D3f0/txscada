from django.core.management.base import NoArgsCommand, CommandError


class Command(NoArgsCommand):
	help = "List profiles"

	def handle_noargs(self, **options):
		from mara.models import Profile
		for profile in Profile.objects.all():
			print "[%s] %s" % ("*" if profile.default else ' ', profile.name, )