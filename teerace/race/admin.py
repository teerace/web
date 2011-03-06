from django.contrib import admin
from race import tasks
from race.forms import ServerAdminForm
from race.models import Map, Server


class MapAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'author', 'crc', 'map_type')
	list_display_links = ('id', 'name')
	fields = ('name', 'author', 'map_file')

	def save_model(self, request, obj, form, change):
		if not change:
			obj.added_by = request.user
		obj.save()
		tasks.retrieve_map_details.apply_async(args=[obj.id], countdown=10)


class ServerAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'maintained_by', 'is_active', 'api_key')
	list_display_links = ('id', 'name')
	list_filter = ('is_active', )
	form = ServerAdminForm

	def add_view(self, request):
		self.exclude = ('api_key', 'played_map', 'anonymous_players')
		return super(ServerAdmin, self).add_view(request)

	def change_view(self, request, obj_id):
		self.exclude = ('played_map', 'anonymous_players')
		#self.readonly_fields = ('api_key', )
		return super(ServerAdmin, self).change_view(request, obj_id)

	def save_model(self, request, obj, form, change):
		if '_regenerate_api' in request.POST:
			obj.regenerate_api_key()
			del request.POST['_regenerate_api']
		obj.save()

	def suspend_server(self, request, queryset):
		queryset.update(is_active=False)
	suspend_server.short_description = "Suspend selected servers"

	def reactivate_server(self, request, queryset):
		queryset.update(is_active=True)
	reactivate_server.short_description = "Reactivate selected servers"

	actions = [suspend_server, reactivate_server]


admin.site.register(Map, MapAdmin)
admin.site.register(Server, ServerAdmin)
