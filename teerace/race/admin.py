from django.contrib import admin
from race.models import Server

class ServerAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'maintained_by', 'public_key')
	list_display_links = ('id', 'name')
	fields = ('name', 'description', 'maintained_by')

admin.site.register(Server, ServerAdmin)
