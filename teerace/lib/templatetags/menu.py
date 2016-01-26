import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def current(request, pattern):
	if pattern == "/":
		if request.path == pattern:
			return mark_safe(' id="current"')
		else:
			return ''
	if request.path.startswith(pattern):
		return mark_safe(' id="current"')
	return ''


@register.simple_tag
def current_unique(request, pattern, element_id):
	if re.search(pattern, request.path):
		return mark_safe(' id="%s-current"' % element_id)
	return mark_safe(' id="%s"' % element_id)
