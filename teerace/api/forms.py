from django import forms
from django.contrib.auth.models import User
from accounts.models import UserProfile
from race.models import Map, Run, BestRun


class UserGetByNameForm(forms.Form):
	username = forms.CharField(max_length=30)


class ValidateUserTokenForm(forms.Form):
	api_token = forms.CharField(min_length=24, max_length=24)


class SkinUserForm(forms.Form):
	"""
	Short explanation of max_value:

	RGB can be stored as one int in format:
		R * 256^2 + G * 256 + B
	Maximum values of R, G and B are 255:
		255 * 256^2 + 255 * 256 + 255 = 16777215
	"""

	skin_name = forms.CharField()
	body_color = forms.IntegerField(max_value=16777215, required=False)
	feet_color = forms.IntegerField(max_value=16777215, required=False)

	def clean_skin_name(self):
		skin_name = self.cleaned_data['skin_name']
		if not skin_name in UserProfile.SKIN_LIST:
			skin_name = 'default'
		return skin_name


class PlaytimeUserForm(forms.Form):
	seconds = forms.IntegerField()


class RunForm(forms.Form):
	map_id = forms.IntegerField()
	user_id = forms.IntegerField()
	nickname = forms.CharField(max_length=15)
	clan = forms.CharField(max_length=11, required=False)
	time = forms.DecimalField(decimal_places=Run.DECIMAL_PLACES,
		max_digits=Run.MAX_DIGITS)
	checkpoints = forms.CharField(required=False)

	def __init__(self, *args, **kwargs):
		super(RunForm, self).__init__(*args, **kwargs)
		self.user = None
		self.map = None

	def clean_map_id(self):
		map_id = self.cleaned_data.get('map_id')
		try:
			self.map = Map.objects.get(pk=map_id)
		except Map.DoesNotExist:
			raise forms.ValidationError("That map doesn't exist.")
		return map_id

	def clean_user_id(self):
		user_id = self.cleaned_data.get('user_id')
		if user_id in (0, None):
			return None
		try:
			self.user = User.objects.get(pk=user_id)
		except User.DoesNotExist:
			raise forms.ValidationError("That user doesn't exist.")
		return user_id


class ActivityForm(forms.ModelForm):
	user_id = forms.IntegerField()
	event_type = forms.CharField(max_length=15)

	def __init__(self, *args, **kwargs):
		super(ActivityForm, self).__init__(*args, **kwargs)
		self.user = None

	def clean_user_id(self):
		user_id = self.cleaned_data.get('user_id')
		if user_id in (0, None):
			return None
		try:
			self.user = User.objects.get(pk=user_id)
		except User.DoesNotExist:
			raise forms.ValidationError("That user doesn't exist.")
		return user_id


class DemoForm(forms.ModelForm):

	class Meta:
		model = BestRun
		fields = ('demo_file', )


class GhostForm(forms.ModelForm):

	class Meta:
		model = BestRun
		fields = ('ghost_file', )


class TokenClientForm(forms.Form):
	username = forms.CharField(max_length=30)
	password = forms.CharField()