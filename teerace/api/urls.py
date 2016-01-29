from django.conf.urls import *
from piston.doc import documentation_view
from api.server_handlers import (RunHandler, UserHandler, MapHandler,
	PingHandler, FileUploadHandler)
from api.client_handlers import AnonClientHandler
from lib.piston_utils import APIKeyAuthentication
from lib.piston_utils import Resource

auth = APIKeyAuthentication(realm="Teerace")
run_resource = Resource(RunHandler, authentication=auth)
user_resource = Resource(UserHandler, authentication=auth)
map_resource = Resource(MapHandler, authentication=auth)
ping_resource = Resource(PingHandler, authentication=auth)
file_resource = Resource(FileUploadHandler, authentication=auth)
anonclient_resource = Resource(AnonClientHandler)

# 1st revision of API
urlpatterns = (
	# Server API
	url(r'^1/runs/detail/(?P<id>\d+)/$', run_resource, {'action': 'detail'},
		name='api_runs_detail'),
	url(r'^1/runs/(?P<action>\w+)/(?P<id>\d+)/$', run_resource, name='api_runs'),
	url(r'^1/runs/(?P<action>\w+)/$', run_resource, name='api_runs'),
	url(r'^1/users/detail/(?P<id>\d+)/$', user_resource, {'action': 'detail'},
		name='api_users_detail'),
	url(r'^1/users/(?P<action>\w+)/(?P<id>\d+)/(?P<map_id>\d+)/$',
		user_resource, name='api_users'),
	url(r'^1/users/(?P<action>\w+)/(?P<id>\d+)/$', user_resource,
		name='api_users'),
	url(r'^1/users/(?P<action>\w+)/$', user_resource, name='api_users'),
	url(r'^1/maps/detail/(?P<map_id>\d+)/$', map_resource, {'action': 'detail'},
		name='api_maps_detail'),
	url(r'^1/maps/(?P<action>\w+)/(?P<map_id>\d+)/(?P<offset>\d+)/$', map_resource,
		name='api_maps'),
	url(r'^1/maps/(?P<action>\w+)/(?P<map_id>\d+)/$', map_resource,
		name='api_maps'),
	url(r'^1/maps/(?P<action>\w+)/(?P<type>\w[-\w\s]*)/$', map_resource,
		name='api_maps'),
	url(r'^1/maps/(?P<action>\w+)/$', map_resource, name='api_maps'),
	url(r'^1/files/(?P<file_type>\w+)/(?P<user_id>\d+)/(?P<map_id>\d+)/$', file_resource,
		name='api_files'),
	url(r'^1/ping/$', ping_resource, {'action': 'ping'}, name='api_ping_post'),
	url(r'^1/hello/$', ping_resource, {'action': 'hello'}, name='api_ping'),

	# Client API
	url(r'^1/anonclient/(?P<action>\w+)/$', anonclient_resource,
		name='api_anonclient'),

	# automated documentation
	url(r'^1/docs/$', documentation_view, name='api_docs'),
)
