from django import forms
from race.models import Server
from lib.widgets import SubmitTextWidget


class ServerAdminForm(forms.ModelForm):

	class Meta:
		fields = ('name', 'description', 'description_html', 'address',
					'maintained_by', 'is_active', 'played_map', 'api_key')
		model = Server
		widgets = {
			'api_key': SubmitTextWidget(name='_regenerate_api',
				label="Regenerate API key"),
		}
