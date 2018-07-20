from django import forms
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe


class SubmitTextWidget(forms.Widget):
    def __init__(self, name, label=None, attrs=None):
        if label is None:
            label = name
        if attrs is None:
            attrs = {}
        self.name, self.label = name, label
        self.attrs = attrs

    def render(self, name, value, attrs=None):
        extra_attrs = dict(type="submit", name=name)
        if self.attrs:
            extra_attrs.update(self.attrs)
        final_attrs = self.build_attrs(attrs, extra_attrs=extra_attrs)
        return mark_safe(
            '<input type="hidden" name="{0}" value="{1}">'
            "<span>{1}</span><button{2}>{3}</button>".format(
                name, value, flatatt(final_attrs), self.label
            )
        )
