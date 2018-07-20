from django import template


register = template.Library()


@register.simple_tag
def possessive(string):
    return "'" if string.endswith("s") else "'s"
