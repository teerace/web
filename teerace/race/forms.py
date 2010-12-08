from django import forms
from race.models import Server
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