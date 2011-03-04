from django import forms
from beta.models import BetaKey


class BetaForm(forms.Form):
	key = forms.CharField(label="Beta key")

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		if self.request is None:
			raise AttributeError("request missing")
		super(BetaForm, self).__init__(*args, **kwargs)
		self.beta_key = None

	def clean_key(self):
		try:
			self.beta_key = BetaKey.objects.get(key=self.cleaned_data.get('key'))
		except BetaKey.DoesNotExist:
			raise forms.ValidationError("Wrong key!")
		if self.beta_key.is_used:
			raise forms.ValidationError("That key has been used already!")

	def save(self):
		self.request.session['is_in_beta'] = True
		self.beta_key.is_used = True
		self.beta_key.save()


class MoarKeysForm(forms.Form):
	keys_num = forms.IntegerField(label="Number of keys to generate",
		min_value=1, max_value=10)

	def __init__(self, *args, **kwargs):
		super(MoarKeysForm, self).__init__(*args, **kwargs)
		self.new_keys = []

	def save(self):
		n = self.cleaned_data.get('keys_num')
		while n:
			k = BetaKey.objects.create()
			self.new_keys.append(k.key)
			n -= 1
