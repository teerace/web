from django.core.management.base import BaseCommand
from race.models import Map
from race import tasks


class Command(BaseCommand):
	help = "Forces the map/global rank rebuild"

	def handle(self, *args, **options):
		maps = Map.objects.all()
		for map_obj in maps:
			tasks.rebuild_map_rank.delay(map_obj.id)
			self.stdout.write("Assigned rank rebuild of \"{0}\" map\n".format(
				map_obj.name)
			)
		tasks.rebuild_global_rank.delay()
		self.stdout.write("Assigned global rank rebuild\n")
