import re
from django import template
from race.models import Run

register = template.Library()

@register.simple_tag
def race_diff(run, compare_to=None, custom_green=None):
	if run == compare_to:
		# sneaky, we use it for race_diff(run, custom_green)
		compare_to = None
	if compare_to is None:
		user = run.user
		map = run.map
		best_result = Run.objects.filter(map=map, user=user).order_by('time')[0]
		diff = run.time - best_result.time
	else:
		diff = run.time - compare_to.time
	if diff > 0.0:
		style = 'red'
	else:
		style = 'green'
		if custom_green:
			return custom_green
	return '<span class="{0}">{1:+.2f}</span>'.format(style, diff)


@register.simple_tag
def diff_color(diff):
	if diff > 0.0:
		style = 'red'
	elif diff < 0.0:
		style = 'green'
	else:
		return '{0:.2f}'.format(diff)
	return '<span class="{0}">{1:+.2f}</span>'.format(style, diff)
	