from django import template
from subprocess import Popen, PIPE

register = template.Library ()

cmd = ["git", "rev-list", "--pretty=short", "master"]

@register.simple_tag
def revision (len = 40):
	p = Popen (cmd, stdout=PIPE).communicate ()[0]
	rev = p.splitlines ()[0][7:]
	return "r<a href=\"https://github.com/chaosk/teerace/commit/%s\">%s</a>" % \
		(rev, rev[:7])