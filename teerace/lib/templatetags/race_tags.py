from decimal import Decimal
from django import template
from race.models import BestRun, Map, Run

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
	return bestrun.points if bestrun else ''


@register.filter
def map_time(player, map_name):
	bestrun = get_best_run(player, map_name)
	return bestrun.time if bestrun else ''


@register.simple_tag
def race_diff(run, compare_to):
	diff = run.time - compare_to.time
	if diff > Decimal('0'):
		style = 'red'
	elif diff < Decimal('0'):
		style = 'green'
	else:
		return '-'
	return '<span class="{0}">{1:+.{precision}f}</span>'.format(style, diff,
		precision=Run.DECIMAL_PLACES)
