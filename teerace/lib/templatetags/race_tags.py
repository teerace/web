from django import template
from race.models import BestRun, Map
from annoying.functions import get_object_or_None

register = template.Library()


def get_best_run(player, map_name):
	try:
		map_obj = Map.objects.get(name=map_name)
		bestrun = BestRun.objects.get(user=player, map=map_obj)
	except (Map.DoesNotExist, BestRun.DoesNotExist):
		return False
	return bestrun


@register.filter
def map_points(player, map_name):
	bestrun = get_best_run(player, map_name)
	return bestrun.points if bestrun else False


@register.filter
def map_time(player, map_name):
	bestrun = get_best_run(player, map_name)
	return bestrun.time if bestrun else False
