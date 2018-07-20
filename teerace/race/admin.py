from django.contrib import admin

from . import tasks
from .forms import MapAdminForm, ServerAdminForm
from .models import Map, MapType, Run, Server


class MapAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "crc", "video")
    list_display_links = ("id", "name")
    list_filter = ("map_types",)
    form = MapAdminForm

    def save_model(self, request, obj, form, change):
        if not change:
            obj.added_by = request.user
        obj.save()
        tasks.retrieve_map_details.apply_async(args=[obj.id], countdown=10)

    def clear_runs(self, request, queryset):
        map_ids = queryset.values_list("id", flat=True)
        Run.objects.filter(map__in=map_ids).delete()

    clear_runs.short_description = "Clear runs of selected maps (IRREVERSIBLE)"

    actions = [clear_runs]


class MapTypeAdmin(admin.ModelAdmin):
    list_display = ("displayed_name", "slug")
    list_display_links = ("displayed_name",)
    fields = ("displayed_name", "description")


class ServerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "maintained_by", "is_active", "api_key")
    list_display_links = ("id", "name")
    list_filter = ("is_active",)
    form = ServerAdminForm

    def add_view(self, request):
        self.exclude = ("api_key", "played_map", "anonymous_players")
        return super().add_view(request)

    def change_view(self, request, obj_id):
        self.exclude = ("played_map", "anonymous_players")
        # self.readonly_fields = ('api_key', )
        return super().change_view(request, obj_id)

    def save_model(self, request, obj, form, change):
        if "_regenerate_api" in request.POST:
            obj.regenerate_api_key()
            del request.POST["_regenerate_api"]
        obj.save()

    def suspend_server(self, request, queryset):
        queryset.update(is_active=False)

    suspend_server.short_description = "Suspend selected servers"

    def reactivate_server(self, request, queryset):
        queryset.update(is_active=True)

    reactivate_server.short_description = "Reactivate selected servers"

    actions = [suspend_server, reactivate_server]


admin.site.register(Map, MapAdmin)
admin.site.register(MapType, MapTypeAdmin)
admin.site.register(Server, ServerAdmin)
