from django import template
from django.core.cache import cache

register = template.Library()

@register.simple_tag
def revision():
	rev = cache.get('current_revision')
	if rev == None:
		return ""
	return "r<a href=\"https://github.com/chaosk/teerace/commit/%s\">%s</a>" % \
		(rev, rev[:7])