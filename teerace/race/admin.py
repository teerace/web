from django.contrib import admin
from race.models import Map, Server


class MapAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'author')
	list_display_links = ('id', 'name')
	fields = ('name', 'author', 'map_file')

	def save_model(self, request, obj, form, change):
		if not change:
			obj.created_by = request.user
		obj.save()


class ServerAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'maintained_by', 'public_key')
	list_display_links = ('id', 'name')
	fields = ('name', 'description', 'maintained_by')

admin.site.register(Map, MapAdmin)
admin.site.register(Server, ServerAdmin)
