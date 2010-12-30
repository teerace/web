from django.contrib import admin
from blog.models import Entry


class EntryAdmin(admin.ModelAdmin):
	list_display = ('title', 'created_at', 'created_by', 'is_published')
	list_display_links = ('created_at', 'title')
	list_filter = ('is_published', 'created_at')
	fields = ('title', 'excerpt', 'content', 'is_published')

	def save_model(self, request, obj, form, change):
		if not change:
			obj.created_by = request.user
		obj.save()

admin.site.register(Entry, EntryAdmin)