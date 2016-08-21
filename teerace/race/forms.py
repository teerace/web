import re
from django import forms
from race.models import Map, Server
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


class MapAdminForm(forms.ModelForm):

	class Meta:
		fields = ('name', 'author', 'map_types', 'map_file', 'video')
		model = Map

	def clean_video(self):
		video = self.cleaned_data['video']
		regex = re.match(r'http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?[\w\?=]*)?', video)
		if not regex:
			raise forms.ValidationError('Video link must be a valid youtube link.')
		if not regex.group(1):
			raise forms.ValidationError('Video id must be given in the link.')
		video = 'https://www.youtube.com/embed/{0}'.format(regex.group(1))
		return video
