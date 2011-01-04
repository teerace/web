from django import forms
from django.contrib.auth.models import User
from race.models import Map, Server
from lib.widgets import SubmitTextWidget


class ServerAdminForm(forms.ModelForm):

	class Meta:
		model = Server
		widgets = {
			'public_key': SubmitTextWidget(name='_regenerate_public',
				label="Regenerate public key"),
			'private_key': SubmitTextWidget(name='_regenerate_private',
				label="Regenerate private key"),
		}


class RunForm(forms.Form):
	no_weapons = forms.BooleanField(required=False)
	map_name = forms.CharField()
	user_id = forms.IntegerField()
	nickname = forms.CharField()
	time = forms.FloatField()

	def __init__(self, *args, **kwargs):
		super(RunForm, self).__init__(*args, **kwargs)
		self.user = None
		self.map = None

	def clean_map_name(self):
		map_name = self.cleaned_data.get('map_name')
		if self.cleaned_data.get('no_weapons', False):
			map_name = '{0}-noweapon'.format(map_name)
		try:
			self.map = Map.objects.get(name=map_name)
		except Map.DoesNotExist:
			raise forms.ValidationError("That map doesn't exist.")
		return map_name

	def clean_user_id(self):
		user_id = self.cleaned_data.get('user_id')
		try:
			self.user = User.objects.get(pk=user_id)
		except User.DoesNotExist:
			raise forms.ValidationError("That user doesn't exist.")
		return user_id
