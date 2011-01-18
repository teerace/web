from django import forms
from accounts.models import UserProfile


class ValidateUserForm(forms.Form):
	username = forms.CharField(max_length=30)
	password = forms.CharField()


class ValidateUserTokenForm(forms.Form):
	api_token = forms.CharField(min_length=32, max_length=32)


class SkinUserForm(forms.Form):
	skin_name = forms.CharField()
	"""
	Short explanation of max_value:

	RGB can be stored as one int in format:
		R * 256^2 + G * 256 + B
	Maximum values of R, G and B are 255:
		255 * 256^2 + 255 * 256 + 255 = 16777215
	"""
	body_color = forms.IntegerField(max_value=16777215)
	feet_color = forms.IntegerField(max_value=16777215)

	def clean_skin_name(self):
		skin_name = self.cleaned_data['skin_name']
		if not skin_name in UserProfile.SKIN_LIST:
			skin_name = 'default'
		return skin_name
