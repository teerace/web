from django.contrib import admin
from race import tasks
from race.forms import ServerAdminForm
from race.models import Map, Server


class MapAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'author', 'crc', 'get_map_type_display')
	list_display_links = ('id', 'name')
	fields = ('name', 'author', 'map_file')

	def save_model(self, request, obj, form, change):
		if not change:
			obj.added_by = request.user
		obj.save()
		tasks.retrieve_map_details.delay(obj.id)


class ServerAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'maintained_by', 'public_key')
	list_display_links = ('id', 'name')
	form = ServerAdminForm

	def add_view(self, request):
		self.exclude = ('public_key', 'private_key')
		return super(ServerAdmin, self).add_view(request)

	def change_view(self, request, obj_id):
		#self.readonly_fields = ('public_key', 'private_key')
		return super(ServerAdmin, self).change_view(request, obj_id)

	def save_model(self, request, obj, form, change):
		if '_regenerate_public' in request.POST:
			obj.regenerate_public_key()
			del request.POST['_regenerate_public']
		if '_regenerate_private' in request.POST:
			obj.regenerate_private_key()
			del request.POST['_regenerate_private']
		obj.save()


admin.site.register(Map, MapAdmin)
admin.site.register(Server, ServerAdmin)
