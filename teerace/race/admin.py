from django.contrib import admin
from race.models import Server

class ServerAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	list_display_links = ('id', 'name')

admin.site.register(Server, ServerAdmin)
