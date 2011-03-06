from django.contrib import admin
from blog.models import Entry


class EntryAdmin(admin.ModelAdmin):
	list_display = ('title', 'created_at', 'created_by', 'is_published')
	list_display_links = ('created_at', 'title')
	list_filter = ('is_published', 'created_at')
	fields = ('title', 'created_by', 'excerpt', 'content',
		'is_published', 'enable_comments')

	def add_view(self, request):
		self.exclude = ('created_by',)
		return super(EntryAdmin, self).add_view(request)

	def save_model(self, request, obj, form, change):
		if not change:
			obj.created_by = request.user
		obj.save()

	def publish_entry(self, request, queryset):
		queryset.update(is_published=True)
	publish_entry.short_description = "Publish selected entries"

	def unpublish_entry(self, request, queryset):
		queryset.update(is_published=False)
	unpublish_entry.short_description = "Unpublish selected entries"

	actions = [publish_entry, unpublish_entry]

admin.site.register(Entry, EntryAdmin)