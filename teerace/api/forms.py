from django import forms


class ValidateUserForm(forms.Form):
	username = forms.CharField(max_length=30)
	password = forms.CharField()
