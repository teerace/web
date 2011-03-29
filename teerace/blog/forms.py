from django import forms
from blog.models import Entry


class EntryAdminForm(forms.ModelForm):

	class Meta:
		model = Entry
		fields = ('title', 'created_by', 'excerpt', 'content',
			'status', 'is_micro', 'enable_comments')

