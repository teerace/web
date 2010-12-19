import re
from django import template

register = template.Library()

@register.simple_tag
def current(request, pattern):
	if pattern == "/":
		if request.path == pattern:
			return ' id="current"'
		else:
			return ''
	if request.path.startswith(pattern):
		return ' id="current"'
	return ''


@register.simple_tag
def current_unique(request, pattern, element_id):
	if re.search(pattern, request.path):
		return ' id="%s-current"' % element_id
	return ' id="%s"' % element_id
