from collections import namedtuple

from django import template

register = template.Library()


Unit = namedtuple("Unit", ["name", "plural", "seconds"])

second = Unit("sec", "secs", 1)
units = [
    Unit("day", "days", 24 * 60 * 60),
    Unit("hr", "hrs", 60 * 60),
    Unit("min", "mins", 60),
]


def _duration_unit(value, unit):
    unit_name = unit.name if value == 1 else unit.plural
    return f"{value:g} {unit_name}"


def _pretty_durations(value):
    remainder = value
    for unit in units:
        quotient, remainder = divmod(remainder, unit.seconds)
        if quotient:
            quotient = int(quotient)
            yield _duration_unit(quotient, unit)
    if remainder:
        yield _duration_unit(remainder, second)


@register.filter
def sectodur(value):
    """Returns human-readable duration from seconds.
    """
    if value <= 0:
        return "-"
    return " ".join(unit for unit in _pretty_durations(value))
