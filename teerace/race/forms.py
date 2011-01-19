from django import forms
from race.models import Server
from lib.widgets import SubmitTextWidget


class ServerAdminForm(forms.ModelForm):

	class Meta:
		model = Server
		widgets = {
			'api_key': SubmitTextWidget(name='_regenerate_api',
				label="Regenerate API key"),
		}
