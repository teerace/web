from django import forms
from django.utils.safestring import mark_safe


class SubmitTextWidget(forms.Widget):
	def __init__(self, name, label=None, attrs=None):
		if label == None:
			label = name
		if attrs == None:
			attrs = {}
		self.name, self.label = name, label
		self.attrs = attrs
		

	def render(self, name, value, attrs=None):
		final_attrs = self.build_attrs(
			self.attrs,
			type="submit",
			name=self.name,
		)
		return mark_safe(u'<input type="hidden" name="{0}" value="{1}">'
			'<span>{1}</span><button{2}>{3}</button>'.format(
			name,
			value,
			forms.widgets.flatatt(final_attrs),
			self.label,
		))
