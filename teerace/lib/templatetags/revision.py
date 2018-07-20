from django import template
from django.utils.safestring import mark_safe

from lib.revision_hook import get_revision


register = template.Library()


@register.simple_tag
def revision():
    rev = get_revision()
    if rev:
        return mark_safe(
            f'r<a href="https://github.com/chaosk/teerace/commit/{rev}">{rev[:7]}</a>'
        )
    return ""
