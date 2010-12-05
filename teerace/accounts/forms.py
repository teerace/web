from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from annoying.functions import get_config
from recaptcha_works.fields import RecaptchaField

class RegisterForm(forms.Form):
	username = forms.RegexField(label="Username", regex=r'^\w+$', min_length=2,
		max_length=30)
	password1 = forms.CharField(label="Password", min_length=4,
		widget=forms.PasswordInput(render_value=False))
	password2 = forms.CharField(label="Password (again)", min_length=4,
		widget=forms.PasswordInput(render_value=False))

	if get_config('ENABLE_CAPTCHA', False):
		if not (get_config('RECAPTCHA_PUBLIC_KEY', False) and
			get_config('RECAPTCHA_PRIVATE_KEY', False)):
			raise ImproperlyConfigured("You must define the RECAPTCHA_PUBLIC_KEY"
				" and/or RECAPTCHA_PRIVATE_KEY setting in order to use reCAPTCHA.")
		recaptcha = RecaptchaField(label="Human test", required=True)

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			user = User.objects.get(username__iexact=username)
			del user
			raise forms.ValidationError("Username is already taken")
		except User.DoesNotExist:
			pass
		return username

	def clean(self):
		if ('password1' in self.cleaned_data and 'password2' in 
			self.cleaned_data):
			password1 = self.cleaned_data['password1']
			password2 = self.cleaned_data['password2']
			if password1 != password2:
				raise forms.ValidationError(
					"You must type the same password each time")
		return self.cleaned_data

	def save(self):
		return User.objects.create_user(self.cleaned_data['username'],
			'', self.cleaned_data['password1'])


class LoginForm(forms.Form):
	username = forms.CharField(label="Username", max_length=30)
	password = forms.CharField(label="Password",
		widget=forms.PasswordInput(render_value=False))

	def __init__(self, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)
		self.user = None

	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')

		if not username or not password:
			return self.cleaned_data
		try:
			self.user = User.objects.get(username__iexact=username)
		except User.DoesNotExist:
			raise forms.ValidationError("Invalid username and/or password")
		if not self.user.check_password(password):
			raise forms.ValidationError("Invalid username and/or password")
		return self.cleaned_data
